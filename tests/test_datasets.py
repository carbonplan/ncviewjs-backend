import json

import pytest

urls = [
    "s3://carbonplan-data-viewer/demo/gpcp_100MB.zarr",
    "s3://carbonplan-data-viewer/demo/AGDC_100MB.zarr",
]

columns = {"id", "url", "bucket", "key", "protocol", "md5_id", "cf_axes", "last_accessed", "size"}


@pytest.mark.parametrize(
    "url,force",
    [(url, force) for url in urls for force in [True, False]],
)
def test_put_store(test_app_with_db, url, force):
    response = test_app_with_db.put(
        '/datasets/',
        content=json.dumps({"url": url, "force": force}),
    )
    assert response.status_code == 201
    data = response.json()
    assert columns.issubset(set(data.keys()))


@pytest.mark.parametrize(
    "url",
    urls,
)
@pytest.mark.parametrize("latest", [True, False])
def test_get_dataset(test_app_with_db, url, latest):

    response = test_app_with_db.put(
        '/datasets/',
        content=json.dumps({"url": url}),
    )

    data = response.json()
    response = test_app_with_db.get(f"/datasets/{data['id']}?latest={latest}")
    assert response.status_code == 200
    data = response.json()
    assert columns.issubset(set(data.keys()))


def test_get_dataset_not_found(test_app_with_db):
    response = test_app_with_db.get(
        '/datasets/3894994',
    )
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]
