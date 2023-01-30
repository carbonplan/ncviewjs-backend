import traceback

import dask.utils
import xarray as xr
from sqlmodel import Session

from .logging import get_logger
from .models.dataset import Dataset, RechunkRun

logger = get_logger()


class DatasetTooLargeError(Exception):
    """Exception raised when the dataset is too large to be processed"""

    def __init__(self, message: str):
        self.message = message


class UnableToOpenDatasetError(Exception):
    """Exception raised when the dataset cannot be opened"""

    def __init__(self, message: str):
        self.message = message


def validate_dataset_size(dataset: xr.Dataset) -> None:
    """Validate that the dataset is not too large to be processed"""

    DATASET_SIZE_THRESHOLD = 60e9  # 60 GB

    if dataset.nbytes > DATASET_SIZE_THRESHOLD:
        dataset_size = dask.utils.format_bytes(dataset.nbytes)
        threshold_size = dask.utils.format_bytes(DATASET_SIZE_THRESHOLD)
        raise DatasetTooLargeError(
            f"""Dataset with ({dataset_size}) exceeds {threshold_size} limit"""
        )


def validate_zarr_store(url: str) -> None:
    """Validate that the Zarr store is accessible"""

    try:
        with xr.open_dataset(url, engine='zarr', chunks={}, decode_cf=False) as ds:
            pass
        del ds

    except DatasetTooLargeError as exc:
        raise DatasetTooLargeError(exc) from exc

    except Exception as exc:
        raise UnableToOpenDatasetError(f'Unable to open Zarr store: {url} due to {exc}') from exc


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


def get_dataset_info(url: str) -> dict[str, str]:
    """Get the dataset info from the store"""
    with xr.open_dataset(url, engine='zarr', chunks={}, decode_cf=False) as ds:
        return {'size': dask.utils.format_bytes(ds.nbytes), 'cf_axes': retrieve_CF_axes(ds)}


def process_dataset(*, dataset: Dataset, rechunk_run: RechunkRun, session: Session) -> None:
    """Validate that the store is accessible and update the dataset in the database"""
    try:
        validate_and_rechunk(dataset=dataset, session=session, rechunk_run=rechunk_run)
    except Exception as exc:

        # update the rechunk run in the database
        rechunk_run.status = "completed"
        rechunk_run.outcome = "failure"
        trace = traceback.format_exc()
        rechunk_run.error_message = trace.splitlines()[-1]
        rechunk_run.error_message_traceback = trace
        _update_entry_in_db(session=session, item=rechunk_run)
        logger.error(f'Rechunking run: {rechunk_run}\nfailed with error: {exc}')
        raise RuntimeError('Dataset processing failed.') from exc


def validate_and_rechunk(*, dataset: Dataset, session: Session, rechunk_run: RechunkRun):
    """Validate the store and rechunk the dataset"""
    rechunk_run.status = 'in_progress'
    _update_entry_in_db(session=session, item=rechunk_run)

    # Update the dataset in the database with the CF axes
    ds_info = get_dataset_info(dataset.url)
    dataset.cf_axes = ds_info['cf_axes']
    dataset.size = ds_info['size']
    _update_entry_in_db(session=session, item=dataset)
    validate_zarr_store(dataset.url)
    logger.info(f'Validation of store: {dataset.url} succeeded')

    # NOTE: Rechunk the dataset: This is currently disabled because we are using the zarr proxy
    # to serve the data. This will be re-enabled if and when we end up with
    # some specific use cases for the persistent rechunking

    # settings = get_settings()
    # endpoint = (
    #     'https://ncview-backend.fly.dev/runs'
    #     if settings.environment == 'prod'
    #     else 'http://localhost:8000/runs'
    # )
    # command = (
    #     f"prefect deployment run rechunk/ncviewjs "
    #     f"--param store_url={dataset.url} "
    #     f"--param key={dataset.key} "
    #     f"--param bucket={dataset.bucket} "
    #     f"--param endpoint={endpoint} "
    #     f"--param rechunk_run_id={rechunk_run.id}"
    # )

    # output = subprocess.check_output(command, shell=True).decode('utf-8')

    # logger.info(f'Output of prefect deployment run: \n{output}')
    logger.info(f'Updating of dataset: {dataset} succeeded')


def _update_entry_in_db(*, session: Session, item: Dataset | RechunkRun):
    session.add(item)
    session.commit()
    session.refresh(item)
