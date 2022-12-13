import json

import pytest

urls = [
    "gs://carbonplan-share/maps-demo/2d/prec-regrid/",
    "https://storage.googleapis.com/carbonplan-share/maps-demo/2d/prec-regrid",
    "s3://carbonplan-share/cmip6-downscaling/DeepSD/",
    "https://carbonplan-share.s3.us-west-2.amazonaws.com/cmip6-downscaling/DeepSD/",
    "az://carbonplan-forests/risks/results/web/fire.zarr",
    "https://carbonplan.blob.core.windows.net/carbonplan-forests/risks/results/web/fire.zarr",
    'gs://cmip6/CMIP6/CMIP/NOAA-GFDL/GFDL-CM4/historical/r1i1p1f1/Omon/thetao/gn/v20180701/',
    'gs://cmip6/CMIP6/CMIP/CCCma/CanESM5/historical/r1i1p1f1/Omon/thetao/gn/v20190429/',
    'gs://cmip6/CMIP6/CMIP/MPI-M/MPI-ESM1-2-HR/historical/r1i1p1f1/Omon/thetao/gn/v20190710/',
]


columns = {
    "id",
    "url",
    "bucket",
    "key",
    "protocol",
    "md5_id",
}


@pytest.mark.parametrize(
    "url",
    urls,
)
def test_put_store(test_app_with_db, url):
    response = test_app_with_db.put(
        '/datasets/',
        content=json.dumps({"url": url}),
    )
    assert response.status_code == 201
    data = response.json()
    assert columns.issubset(set(data.keys()))


@pytest.mark.parametrize(
    "url",
    urls,
)
def test_get_dataset(test_app_with_db, url):

    response = test_app_with_db.put(
        '/datasets/',
        content=json.dumps({"url": url}),
    )

    data = response.json()
    response = test_app_with_db.get(f"/datasets/{data['id']}")
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
