import rechunker
import xarray as xr
import zarr
from prefect import flow, task
from utils import determine_chunk_size


def _retrieve_CF_dims(url: str) -> dict:  # Update this datatype to pydantic model from main
    import cf_xarray  # noqa: F401

    ds = xr.open_zarr(url)
    X = ds.cf['X'].name
    Y = ds.cf['Y'].name
    T = ds.cf['T'].name
    return {'X': X, 'Y': Y, 'T': T}


@task
def rechunk_dataset(
    *,
    zarr_store_url: str,
    cf_dims_dict: dict,
    spatial_chunk_square_size: int = 128,
    target_size_bytes: int = 5e5,
    max_mem: str = "1000MB",
    target_store: str = None,
    temp_store: str = None,
):

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

    array_plan = rechunker.rechunk(group, chunks_dict, max_mem, target_store, temp_store=temp_store)
    array_plan.execute()
    return target_store


@flow
def rechunk_flow(zarr_store_url: str) -> dict:
    cf_dims_dict = _retrieve_CF_dims(zarr_store_url)
    target_store = rechunk_dataset(
        zarr_store_url=zarr_store_url,
        cf_dims_dict=cf_dims_dict,
        target_store='tgt.zarr',
        temp_store='tmp.zarr',
    )

    ds = xr.open_zarr(target_store)
    print(ds)
