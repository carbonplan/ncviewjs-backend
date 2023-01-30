import pytest

from ncviewjs_backend.dataset_processing import (
    UnableToOpenDatasetError,
    validate_zarr_store,
)


def test_unable_to_open_store_error():
    """Test that the Zarr store is accessible"""
    with pytest.raises(UnableToOpenDatasetError):
        validate_zarr_store('https://raw.githubusercontent.com/foo/bar/baz.zarr')
