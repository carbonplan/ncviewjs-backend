import dask.utils
import xarray as xr
from sqlmodel import Session

from .logging import get_logger
from .models.dataset import Dataset, RechunkRun
from .rechunking.rechunk import rechunk_flow

DATASET_SIZE_THRESHOLD = 7e9

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
            validate_dataset_size(ds)
        del ds

    except DatasetTooLargeError as exc:
        raise DatasetTooLargeError(exc) from exc

    except Exception as exc:
        raise UnableToOpenDatasetError(f'Unable to open Zarr store: {url} due to {exc}') from exc


def retrieve_CF_axes(url: str) -> dict[str, dict[str, str]]:
    """Retrieve the CF dimensions from the dataset"""
    import cf_xarray  # noqa

    with xr.open_dataset(url, engine='zarr', chunks={}, decode_cf=False) as ds:

        results = {}
        for variable in ds.data_vars:
            axes = ds[variable].cf.axes
            for key, value in axes.items():
                axes[key] = value[0]
            results[variable] = axes
        return results


def process_dataset(*, dataset: Dataset, rechunk_run: RechunkRun, session: Session) -> None:
    """Validate that the store is accessible and update the dataset in the database"""
    try:
        validate_and_rechunk(dataset=dataset, session=session, rechunk_run=rechunk_run)
    except Exception as exc:

        # update the rechunk run in the database
        rechunk_run.status = "completed"
        rechunk_run.outcome = "failure"
        rechunk_run.error_message = str(exc)
        _update_entry_in_db(session=session, item=rechunk_run)
        logger.error(f'Rechunking run: {rechunk_run}\nfailed with error: {exc}')
        raise RuntimeError('Dataset processing failed.') from exc


def validate_and_rechunk(*, dataset: Dataset, session: Session, rechunk_run: RechunkRun):
    validate_zarr_store(dataset.url)
    # Update the dataset in the database with the CF axes
    cf_axes = retrieve_CF_axes(dataset.url)
    dataset.cf_axes = cf_axes
    _update_entry_in_db(session=session, item=dataset)
    logger.info(f'Validation of store: {dataset.url} succeeded')

    # Rechunk the dataset
    production_store = rechunk_flow(dataset=dataset)
    logger.info(f'Rechunking of store: {dataset.url} succeeded')

    # Update the dataset in the database with the production store
    rechunk_run.status = "completed"
    rechunk_run.outcome = "success"
    rechunk_run.rechunked_dataset = production_store
    _update_entry_in_db(session=session, item=rechunk_run)
    logger.info(f'Updating of dataset: {dataset} succeeded')


def _update_entry_in_db(*, session: Session, item: Dataset | RechunkRun):
    session.add(item)
    session.commit()
    session.refresh(item)