from fastapi.testclient import TestClient


def test_not_found(client: TestClient):
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_method_not_allowed(client: TestClient):
    response = client.post("/health")

    assert response.status_code == 405


def test_users_structure(client: TestClient):
    response = client.get("/users")

    assert response.status_code == 200

    users = response.json()

    assert isinstance(users, list)

    for user in users:
        assert "id" in user
        assert "name" in user
        assert isinstance(user["id"], int)
        assert isinstance(user["name"], str)
