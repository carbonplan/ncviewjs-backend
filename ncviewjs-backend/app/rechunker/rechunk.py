import os

import cf_xarray  # noqa: F401
import fsspec
import rechunker
import xarray as xr
import zarr
from prefect import flow, task
from utils import determine_chunk_size

from app.models.pydantic import SanitizedURL


def _generate_tgt_tmp_stores(sanitized_url: SanitizedURL, processing_type: str) -> dict:
    store_suffix = f"/{processing_type}/{sanitized_url.key}"
    tmp_store = "s3://carbonplan-data-viewer-staging/tmp/" + store_suffix
    staging_store = "s3://carbonplan-data-viewer-staging" + store_suffix
    prod_store = "s3://carbonplan-data-viewer-production" + store_suffix
    return {'temp_store': tmp_store, 'staging_store': staging_store, 'prod_store': prod_store}


def _retrieve_CF_dims(url: str) -> dict:

    ds = xr.open_zarr(url)
    X = ds.cf['X'].name
    Y = ds.cf['Y'].name
    T = ds.cf['T'].name
    return {'X': X, 'Y': Y, 'T': T}


@task
def copy_staging_to_production(store_paths: dict):
    transfer_str = f"skyplane cp -r -y {store_paths['staging_store']} {store_paths['prod_store']}"
    print(transfer_str)
    os.system(transfer_str)


@task
def finalize():
    pass


@task()
def rechunk_dataset(
    *,
    zarr_store_url: str,
    cf_dims_dict: dict,
    store_paths: dict,
    spatial_chunk_square_size: int = 128,
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
        X,Y spatial chunk size by default 128
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

    ds = xr.open_zarr(zarr_store_url)
    group = zarr.open_consolidated(zarr_store_url)
    chunks_dict = {
        cf_dims_dict['T']: (time_chunk,),
        cf_dims_dict['X']: (spatial_chunk_square_size,),
        cf_dims_dict['Y']: (spatial_chunk_square_size,),
    }
    for var in ds.data_vars:
        chunks_dict[var] = {
            cf_dims_dict['T']: time_chunk,
            cf_dims_dict['X']: spatial_chunk_square_size,
            cf_dims_dict['Y']: spatial_chunk_square_size,
        }

    tmp_mapper = fsspec.get_mapper(store_paths['temp_store'])
    tgt_mapper = fsspec.get_mapper(store_paths['staging_store'])

    array_plan = rechunker.rechunk(group, chunks_dict, max_mem, tgt_mapper, temp_store=tmp_mapper)
    array_plan.execute()


@flow(name="rechunking-flow")
def rechunk_flow(sanitized_url: SanitizedURL) -> dict:
    store_paths = _generate_tgt_tmp_stores(sanitized_url, processing_type='rechunked')
    cf_dims_dict = _retrieve_CF_dims(sanitized_url.url)
    rechunk_state = rechunk_dataset(
        zarr_store_url=sanitized_url.url,
        cf_dims_dict=cf_dims_dict,
        store_paths=store_paths,
        return_state=True,
    )
    copy_staging_to_production(store_paths)
    return {'production_store': store_paths['prod_store'], 'error': rechunk_state.message}


# Note: snippet below is for end2end testing
# from app.helpers import sanitize_url

# url = "s3://carbonplan-scratch/gpcp_100MB.zarr"
# sanitized_url = sanitize_url(url)
# result = rechunk_flow(sanitized_url)
