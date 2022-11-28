import json

import pytest

urls = [
    "gs://carbonplan-share/maps-demo/2d/prec-regrid/",
    "https://storage.googleapis.com/carbonplan-share/maps-demo/2d/prec-regrid",
    "s3://carbonplan-share/cmip6-downscaling/DeepSD/",
    "https://carbonplan-share.s3.us-west-2.amazonaws.com/cmip6-downscaling/DeepSD/",
    "az://carbonplan-forests/risks/results/web/fire.zarr",
    "https://carbonplan.blob.core.windows.net/carbonplan-forests/risks/results/web/fire.zarr",
]


@pytest.mark.parametrize(
    "url",
    urls,
)
def test_post_store(test_app_with_db, url):
    response = test_app_with_db.post(
        '/store/',
        content=json.dumps({"url": url}),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["url"] == url.strip("/")
    assert data.keys() == {
        "id",
        "url",
        "last_accessed_at",
        "registered_at",
        "conclusion",
        "status",
        "rechunked_url",
        "bucket",
        "key",
        "protocol",
        "md5_id",
    }


@pytest.mark.parametrize(
    "url",
    urls,
)
def test_get_store(test_app_with_db, url):
    response = test_app_with_db.get(
        '/store/',
        params={"url": url},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == url.strip("/")
    assert data.keys() == {
        "id",
        "url",
        "last_accessed_at",
        "registered_at",
        "conclusion",
        "status",
        "rechunked_url",
        "md5_id",
        "protocol",
        "bucket",
        "key",
    }


def test_get_store_not_found(test_app_with_db):
    url = "gs://foo/bar"
    response = test_app_with_db.get(
        '/store/',
        params={"url": url},
    )
    assert response.status_code == 404
    data = response.json()
    assert f"Store: {url} not found" in data["detail"]
