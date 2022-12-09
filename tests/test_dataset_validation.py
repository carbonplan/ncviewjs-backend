import pytest

from ncviewjs_backend.dataset_validation import (
    DatasetTooLargeError,
    UnableToOpenDatasetError,
    validate_zarr_store,
)


def test_unable_to_open_store_error():
    """Test that the Zarr store is accessible"""
    with pytest.raises(UnableToOpenDatasetError):
        validate_zarr_store('https://raw.githubusercontent.com/foo/bar/baz.zarr')


def test_too_large_store_error():
    """Test that the dataset is not too large to be processed"""
    with pytest.raises(DatasetTooLargeError):
        validate_zarr_store(
            'gs://cmip6/CMIP6/CMIP/NOAA-GFDL/GFDL-CM4/historical/r1i1p1f1/Omon/thetao/gn/v20180701/'
        )
