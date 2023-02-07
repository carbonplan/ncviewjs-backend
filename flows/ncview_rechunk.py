import datetime
import subprocess
from platform import node, platform, python_version

import prefect
import pydantic
import requests
import xarray as xr
from prefect.orion.api.server import ORION_API_VERSION as API


def determine_chunk_size(spatial_chunk_square_size: int = 256, target_size_bytes: int = 5e5) -> int:
    return round(target_size_bytes / 4 / spatial_chunk_square_size**2)


def retrieve_CF_axes(ds: xr.Dataset) -> dict[str, dict[str, str]]:
    """Retrieve the CF dimensions from the dataset"""
    import cf_xarray  # noqa

    results = {}
    for variable in ds.variables:
        axes = ds[variable].cf.axes
        for key, value in axes.items():
            axes[key] = value[0]
        results[variable] = axes
    return results


@prefect.task
def initialize_skyplane():
    logger = prefect.get_run_logger()
    logger.info("Initializing skyplane...")
    subprocess.check_call(
        "skyplane init -y --disable-config-azure --disable-config-gcp", shell=True
    )
    logger.info("Successfully initialized skyplane")


@prefect.task
def copy_staging_to_production(*, staging_store: pydantic.AnyUrl, prod_store: pydantic.AnyUrl):
    logger = prefect.get_run_logger()
    transfer_str = f"skyplane cp -r -y {staging_store} {prod_store}"
    logger.info(f"Copying staging store to production store: {transfer_str}")
    subprocess.check_call(transfer_str, shell=True)
    logger.info("Successfully copied staging store to production store")


@prefect.task
def dataset_is_valid(*, zarr_store_url: pydantic.HttpUrl):
    """Checks that rechunked dataset is valid."""

    try:
        with xr.open_dataset(zarr_store_url, engine='zarr', chunks={}, decode_cf=False):
            pass
    except Exception as exc:
        raise RuntimeError(f'Error opening rechunked dataset: {zarr_store_url}') from exc


@prefect.task
def agent_info():
    version = prefect.__version__
    logger = prefect.get_run_logger()
    logger.info('Network: %s. Instance: %s. Agent is healthy ✅️', node(), platform())
    logger.info('Python = %s. API: %s. Prefect = %s 🚀', python_version(), API, version)


@prefect.task
def process_dataset(
    *,
    store_url: pydantic.AnyUrl,
    store_paths: dict,
    spatial_chunk_square_size: int = 256,
    target_size_bytes: int = 5e5,
    max_mem: str = "1000MB",
):
    """Rechunks zarr dataset to match chunk schema required by carbonplan web-viewer."""
    import fsspec
    import rechunker
    import zarr
    from prefect_aws.credentials import AwsCredentials

    logger = prefect.get_run_logger()
    logger.info('ncview rechunking is running 🚀')
    logger.info('store_url = %s', store_url)

    time_chunk = determine_chunk_size(
        spatial_chunk_square_size=spatial_chunk_square_size, target_size_bytes=target_size_bytes
    )

    start_time = datetime.datetime.now(datetime.timezone.utc)

    ds = xr.open_dataset(store_url, engine='zarr', chunks={}, decode_cf=False)
    group = zarr.open_consolidated(store_url)
    cf_axes_dict = retrieve_CF_axes(ds)
    logger.info(f'Opened dataset: {ds}')

    chunks_dict = {}
    for variable, axes in cf_axes_dict.items():
        variable_dims = ds[variable].dims
        sizes = ds[variable].sizes

        result = {}
        for key, value in axes.items():
            if key == 'T':
                result[value] = min(time_chunk, sizes[value])
            elif key in ['X', 'Y']:
                result[value] = min(spatial_chunk_square_size, sizes[value])
        for dim in variable_dims:
            if dim not in result.keys():
                result[dim] = sizes[dim]

        chunks_dict[variable] = result

    logger.info(f'Chunks: {chunks_dict}')

    creds = AwsCredentials.load('prod')

    storage_options = {
        'anon': False,
        'key': creds.aws_access_key_id,
        'secret': creds.aws_secret_access_key.get_secret_value(),
    }

    tmp_mapper = fsspec.get_mapper(store_paths['temp_store'], **storage_options)
    tgt_mapper = fsspec.get_mapper(store_paths['staging_store'], **storage_options)

    array_plan = rechunker.rechunk(group, chunks_dict, max_mem, tgt_mapper, temp_store=tmp_mapper)
    array_plan.execute()

    # Consolidate metadata
    zarr.consolidate_metadata(store_paths['staging_store'])
    end_time = datetime.datetime.now(datetime.timezone.utc)
    return start_time, end_time


@prefect.task
def generate_stores(
    *,
    key: str,
    bucket: str,
    scratch_bucket: pydantic.AnyUrl,
    staging_bucket: pydantic.AnyUrl,
    production_bucket: pydantic.AnyUrl,
):
    # TODO: use a better naming scheme
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H-%M-%S')
    store_suffix = f"{now}/{bucket}/{key}"
    tmp_store = f"{scratch_bucket}/{store_suffix}"
    staging_store = f"{staging_bucket}/{store_suffix}"
    prod_store = f"{production_bucket}/{store_suffix}"
    return {'temp_store': tmp_store, 'staging_store': staging_store, 'prod_store': prod_store}


@prefect.task(retries=3, retry_delay_seconds=3)
def finalize(
    *,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    rechunked_dataset: pydantic.AnyUrl,
    url: pydantic.AnyHttpUrl,
):
    logger = prefect.get_run_logger()

    # Send a post request to ncview-backend.fly.dev/datasets/ with the start and end time
    # to trigger a reindexing of the dataset

    data = {
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'rechunked_dataset': rechunked_dataset,
        'status': "completed",
        'outcome': "success",
    }

    try:
        requests.patch(
            url,
            json=data,
        )
        logger.info(f'Sent request to {url} 🚀 with data: {data}')

    except Exception as exc:
        logger.info(f'Failed to send request to {url} with data: {data} with error: {exc}')

    logger.info('ncview rechunking is done 🚀')
    logger.info('Total time: %s', end_time - start_time)


@prefect.flow(description='Rechunking flow for ncviewjs')
def rechunk(
    store_url: pydantic.AnyUrl,
    key: str,
    bucket: str,
    rechunk_run_id: int,
    scratch_bucket: pydantic.AnyUrl = 's3://carbonplan-data-viewer-staging/tmp',
    staging_bucket: pydantic.AnyUrl = 's3://carbonplan-data-viewer-staging',
    production_bucket: pydantic.AnyUrl = 's3://carbonplan-data-viewer-production',
    endpoint: pydantic.AnyHttpUrl = 'https://ncview-backend.fly.dev/runs',
):
    _ = agent_info()
    initialize_skyplane.submit(wait_for=[_])
    store_paths = generate_stores(
        key=key,
        bucket=bucket,
        scratch_bucket=scratch_bucket,
        staging_bucket=staging_bucket,
        production_bucket=production_bucket,
    )

    start_time, end_time = process_dataset(store_url=store_url, store_paths=store_paths)

    # Check that rechunked dataset is valid
    dataset_is_valid(zarr_store_url=store_paths['staging_store'])

    _ = copy_staging_to_production(
        staging_store=store_paths['staging_store'], prod_store=store_paths['prod_store']
    )

    # Check that production dataset is valid
    _ = dataset_is_valid.submit(zarr_store_url=store_paths['prod_store'], wait_for=[_])

    # finalize
    url = f"{endpoint}/{rechunk_run_id}/"
    _ = finalize.submit(
        start_time=start_time,
        end_time=end_time,
        rechunked_dataset=store_paths['prod_store'],
        url=url,
        wait_for=[_],
    )


if __name__ == '__main__':
    rechunk(
        store_url="s3://carbonplan-data-viewer/demo/gpcp_180_180_chunks.zarr",
        key="gpcp_180_180_chunks.zarr",
        bucket="demo",
        rechunk_run_id=1,
        endpoint="http://localhost:8000/runs",
    )
