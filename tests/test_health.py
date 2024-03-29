def test_ping(test_app):
    response = test_app.get("/health/ping")
    assert response.status_code == 200
    assert response.json() == {
        "ping": "pong",
        "environment": "dev",
        "testing": True,
    }
