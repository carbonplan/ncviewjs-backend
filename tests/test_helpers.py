import pytest

from ncviewjs_backend.helpers import sanitize_url


@pytest.mark.parametrize(
    'url, expected_bucket, expected_key',
    [
        ('s3://bucket/key', 'bucket', 'key'),
        (
            'https://carbonplan-data-viewer.s3.us-west-2.amazonaws.com/demo/ScenarioMIP.CCCma.CanESM5.ssp245.r1i1p1f1.day.GARD-SV.tasmax.zarr',
            'carbonplan-data-viewer',
            'demo/ScenarioMIP.CCCma.CanESM5.ssp245.r1i1p1f1.day.GARD-SV.tasmax.zarr',
        ),
        (
            'https://carbonplan-data-viewer.s3.amazonaws.com/demo/ScenarioMIP.CCCma.CanESM5.ssp245.r1i1p1f1.day.GARD-SV.tasmax.zarr/',
            'carbonplan-data-viewer',
            'demo/ScenarioMIP.CCCma.CanESM5.ssp245.r1i1p1f1.day.GARD-SV.tasmax.zarr',
        ),
        (
            'https://storage.googleapis.com/carbonplan-share/maps-demo/2d/prec-regrid',
            'carbonplan-share',
            'maps-demo/2d/prec-regrid',
        ),
        (
            'https://carbonplan.blob.core.windows.net/demo/ScenarioMIP.CCCma.CanESM5.ssp245.r1i1p1f1.day.GARD-SV.tasmax.zarr',
            'carbonplan',
            'demo/ScenarioMIP.CCCma.CanESM5.ssp245.r1i1p1f1.day.GARD-SV.tasmax.zarr',
        ),
    ],
)
def test_sanitize_url(url, expected_bucket, expected_key):
    sanitized_url = sanitize_url(url)
    assert sanitized_url.bucket == expected_bucket
    assert sanitized_url.key == expected_key
