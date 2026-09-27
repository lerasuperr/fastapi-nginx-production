from fastapi.testclient import TestClient


def test_get_users(client: TestClient):
    response = client.get("/users")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "Alice",
        },
        {
            "id": 2,
            "name": "Valeria",
        },
    ]
