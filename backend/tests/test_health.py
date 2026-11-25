from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_unknown_route_uses_standard_shape_or_404():
    response = client.get("/does-not-exist")
    assert response.status_code == 404