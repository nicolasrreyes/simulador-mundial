from fastapi.testclient import TestClient


def test_create_user(client: TestClient):
    res = client.post("/users/", json={"name": "Juan Perez", "email": "juan@test.com"})
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Juan Perez"
    assert data["email"] == "juan@test.com"


def test_create_user_duplicate_email(client: TestClient):
    client.post("/users/", json={"name": "Juan", "email": "juan@test.com"})
    res = client.post("/users/", json={"name": "Pedro", "email": "juan@test.com"})
    assert res.status_code == 409


def test_create_user_invalid_email(client: TestClient):
    res = client.post("/users/", json={"name": "Juan", "email": "not-an-email"})
    assert res.status_code == 422


def test_list_users(client: TestClient):
    client.post("/users/", json={"name": "Juan", "email": "juan@test.com"})
    client.post("/users/", json={"name": "Maria", "email": "maria@test.com"})
    res = client.get("/users/")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_get_user(client: TestClient):
    res = client.post("/users/", json={"name": "Juan", "email": "juan@test.com"})
    user_id = res.json()["id"]
    res = client.get(f"/users/{user_id}")
    assert res.status_code == 200
    assert res.json()["name"] == "Juan"


def test_get_user_not_found(client: TestClient):
    res = client.get("/users/999")
    assert res.status_code == 404


def test_update_user(client: TestClient):
    res = client.post("/users/", json={"name": "Juan", "email": "juan@test.com"})
    user_id = res.json()["id"]
    res = client.put(f"/users/{user_id}", json={"name": "Juan Actualizado", "email": "juan@test.com"})
    assert res.status_code == 200
    assert res.json()["name"] == "Juan Actualizado"


def test_update_user_duplicate_email(client: TestClient):
    client.post("/users/", json={"name": "Juan", "email": "juan@test.com"})
    u2 = client.post("/users/", json={"name": "Maria", "email": "maria@test.com"}).json()
    res = client.put(f"/users/{u2['id']}", json={"name": "Maria", "email": "juan@test.com"})
    assert res.status_code == 409


def test_delete_user(client: TestClient):
    res = client.post("/users/", json={"name": "Juan", "email": "juan@test.com"})
    user_id = res.json()["id"]
    res = client.delete(f"/users/{user_id}")
    assert res.status_code == 204
    res = client.get(f"/users/{user_id}")
    assert res.status_code == 404


def test_delete_user_not_found(client: TestClient):
    res = client.delete("/users/999")
    assert res.status_code == 404


def test_update_user_not_found(client: TestClient):
    res = client.put("/users/999", json={"name": "Ghost", "email": "ghost@test.com"})
    assert res.status_code == 404
