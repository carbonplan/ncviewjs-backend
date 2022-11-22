import shutil

import rechunker
import xarray as xr
import zarr
from prefect import flow, task
from utils import determine_chunk_size


@task
def rechunk_dataset(
    *,
    zarr_store_url: str,
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
        "time": (time_chunk,),
        "longitude": (spatial_chunk_square_size,),
        "latitude": (spatial_chunk_square_size,),
    }
    for var in ds.data_vars:
        chunks_dict[var] = {
            "time": time_chunk,
            "longitude": spatial_chunk_square_size,
            "latitude": spatial_chunk_square_size,
        }

    # update this. Check if temp store exists, if so, wipe
    shutil.rmtree(target_store)
    shutil.rmtree(temp_store)

    # need to remove the existing stores or it won't work
    array_plan = rechunker.rechunk(group, chunks_dict, max_mem, target_store, temp_store=temp_store)
    array_plan.execute()
    return target_store


@flow
def rechunk_flow():
    target_store = rechunk_dataset(
        zarr_store_url='s3://carbonplan-data-viewer/demo/gpcp_100MB.zarr',
        target_store='tgt.zarr',
        temp_store='tmp.zarr',
    )
    ds = xr.open_zarr(target_store)
    print(ds)
