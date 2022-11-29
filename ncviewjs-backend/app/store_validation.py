import dask.utils
import xarray as xr

DATASET_SIZE_THRESHOLD = 1e9


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
