from fastapi.testclient import TestClient

from securebank.main import app

client = TestClient(app)


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_scalar_docs(client):
    response = client.get("/scalar")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

