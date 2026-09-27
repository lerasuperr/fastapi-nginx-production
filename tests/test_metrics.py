from fastapi.testclient import TestClient


def test_metrics(client: TestClient):
    response = client.get("/metrics")

    assert response.status_code == 200

    body = response.text

    assert "api_requests_total" in body
    assert "api_request_duration_seconds" in body
