import os
import subprocess
import uuid

import fsspec
import pydantic
import rechunker
import xarray as xr
import zarr

from ..config import get_settings
from ..helpers import s3_to_https
from ..models.dataset import Dataset
from .utils import determine_chunk_size


def copy_staging_to_production(*, staging_store: pydantic.AnyUrl, prod_store: pydantic.AnyUrl):
    transfer_str = f"skyplane cp -r -y {staging_store} {prod_store}"
    print(transfer_str)
    subprocess.check_output(transfer_str, shell=True)


def dataset_is_valid(*, zarr_store_url: pydantic.HttpUrl):
    """Checks that rechunked dataset is valid."""
    try:
        with xr.open_dataset(zarr_store_url, engine='zarr', chunks={}, decode_cf=False):
            pass
    except Exception as exc:
        raise RuntimeError(f'Error opening rechunked dataset: {zarr_store_url}') from exc


def rechunk_dataset(
    *,
    zarr_store_url: str,
    cf_axes_dict: dict,
    store_paths: dict,
    spatial_chunk_square_size: int = 256,
    target_size_bytes: int = 5e5,
    max_mem: str = "1000MB",
):
    """Rechunks zarr dataset to match chunk schema required by carbonplan web-viewer.

    Parameters
    ----------
    zarr_store_url : str
        Input zarr store url to be rechunked
    cf_dims_dict : dict
        dictionary of CF dims
    store_paths : dict
        rechunker temp and target paths
    spatial_chunk_square_size : int, optional
        X,Y spatial chunk size by default 256
    target_size_bytes : int, optional
        target size in bytes, by default 5e5
    max_mem : str, optional
        max memory available for rechunking operation, by default "1000MB"

    Returns
    -------
    str
        path to rechunked target store
    """

    time_chunk = determine_chunk_size(
        spatial_chunk_square_size=spatial_chunk_square_size, target_size_bytes=target_size_bytes
    )

    ds = xr.open_dataset(zarr_store_url, engine='zarr', chunks={}, decode_cf=False)
    print(ds)
    group = zarr.open_consolidated(zarr_store_url)

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
                result[dim] = -1

        chunks_dict[variable] = result

    print(f'Chunks: {chunks_dict}')

    storage_options = {
        'aws_access_key_id': os.environ['AWS_ACCESS_KEY_ID'],
        'aws_secret_access_key': os.environ['AWS_SECRET_ACCESS_KEY'],
    }

    tmp_mapper = fsspec.get_mapper(store_paths['temp_store'], **storage_options)
    tgt_mapper = fsspec.get_mapper(store_paths['staging_store'], **storage_options)

    array_plan = rechunker.rechunk(group, chunks_dict, max_mem, tgt_mapper, temp_store=tmp_mapper)
    array_plan.execute()

    # Consolidate metadata
    zarr.consolidate_metadata(store_paths['staging_store'])

    # Check that rechunked dataset is valid
    dataset_is_valid(zarr_store_url=store_paths['staging_store'])


def generate_stores(*, key: str, bucket: str, md5_id: str):
    settings = get_settings()
    # TODO: use a better naming scheme
    store_suffix = f"{uuid.uuid1()}-{md5_id}.zarr"
    tmp_store = f"{settings.scratch_bucket}/{store_suffix}"
    staging_store = f"{settings.staging_bucket}/{store_suffix}"
    prod_store = f"{settings.production_bucket}/{store_suffix}"
    return {'temp_store': tmp_store, 'staging_store': staging_store, 'prod_store': prod_store}


def rechunk_flow(*, dataset: Dataset) -> pydantic.HttpUrl:
    """Rechunks zarr dataset to match chunk schema required by carbonplan web-viewer.

    Parameters
    ----------
    dataset : Dataset
        Dataset object to be rechunked

    Returns
    -------
    pydantic.HttpUrl
        https url to rechunked target store
    """
    store_paths = generate_stores(key=dataset.key, bucket=dataset.bucket, md5_id=dataset.md5_id)
    rechunk_dataset(
        zarr_store_url=dataset.url, cf_axes_dict=dataset.cf_axes, store_paths=store_paths
    )

    copy_staging_to_production(
        staging_store=store_paths['staging_store'], prod_store=store_paths['prod_store']
    )

    return s3_to_https(s3_url=store_paths['prod_store'])
