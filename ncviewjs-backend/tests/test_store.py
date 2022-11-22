import json

import pytest


@pytest.mark.parametrize(
    "url",
    ["gs://cmip6/CMIP6/CMIP/NOAA-GFDL/GFDL-CM4/historical/r1i1p1f1/Omon/thetao/gn/v20180701/"],
)
def test_post_store(test_app_with_db, url):
    response = test_app_with_db.post(
        '/store/',
        content=json.dumps({"url": url}),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["url"] == url
    assert data.keys() == {
        "id",
        "url",
        "last_accessed_at",
        "registered_at",
        "conclusion",
        "status",
        "rechunked_url",
    }


@pytest.mark.parametrize(
    "url",
    ["gs://cmip6/CMIP6/CMIP/NOAA-GFDL/GFDL-CM4/historical/r1i1p1f1/Omon/thetao/gn/v20180701/"],
)
def test_get_store(test_app_with_db, url):
    response = test_app_with_db.get(
        '/store/',
        params={"url": url},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == url
    assert data.keys() == {
        "id",
        "url",
        "last_accessed_at",
        "registered_at",
        "conclusion",
        "status",
        "rechunked_url",
    }
