from fastapi.testclient import TestClient


def test_create_team(client: TestClient):
    res = client.post("/teams/", json={"name": "Argentina", "code": "ARG"})
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Argentina"
    assert data["code"] == "ARG"


def test_create_team_duplicate_code(client: TestClient):
    client.post("/teams/", json={"name": "Argentina", "code": "ARG"})
    res = client.post("/teams/", json={"name": "Brasil", "code": "ARG"})
    assert res.status_code == 409


def test_list_teams(client: TestClient):
    client.post("/teams/", json={"name": "Argentina", "code": "ARG"})
    client.post("/teams/", json={"name": "Brasil", "code": "BRA"})
    res = client.get("/teams/")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_get_team(client: TestClient):
    res = client.post("/teams/", json={"name": "Argentina", "code": "ARG"})
    team_id = res.json()["id"]
    res = client.get(f"/teams/{team_id}")
    assert res.status_code == 200
    assert res.json()["name"] == "Argentina"


def test_get_team_not_found(client: TestClient):
    res = client.get("/teams/999")
    assert res.status_code == 404


def test_update_team(client: TestClient):
    res = client.post("/teams/", json={"name": "Argentina", "code": "ARG"})
    team_id = res.json()["id"]
    res = client.put(f"/teams/{team_id}", json={"name": "Argentina Actualizado"})
    assert res.status_code == 200
    assert res.json()["name"] == "Argentina Actualizado"


def test_delete_team(client: TestClient):
    res = client.post("/teams/", json={"name": "Argentina", "code": "ARG"})
    team_id = res.json()["id"]
    res = client.delete(f"/teams/{team_id}")
    assert res.status_code == 204
    res = client.get(f"/teams/{team_id}")
    assert res.status_code == 404


def test_create_team_duplicate_name_returns_409(client: TestClient):
    client.post("/teams/", json={"name": "Argentina", "code": "ARG"})
    res = client.post("/teams/", json={"name": "Argentina", "code": "BRA"})
    assert res.status_code == 409


def test_create_team_code_uppercased(client: TestClient):
    res = client.post("/teams/", json={"name": "Argentina", "code": "arg"})
    assert res.status_code == 201
    assert res.json()["code"] == "ARG"


def test_delete_team_cascades_players(client: TestClient):
    team = client.post("/teams/", json={"name": "Argentina", "code": "ARG"}).json()
    client.post("/players/", json={"name": "Messi", "position": "FW", "team_id": team["id"]})
    player_res = client.get(f"/players/?team_id={team['id']}")
    assert len(player_res.json()) == 1
    client.delete(f"/teams/{team['id']}")
    player_res = client.get(f"/players/?team_id={team['id']}")
    assert player_res.json() == []


def test_create_team_empty_name_returns_422(client: TestClient):
    res = client.post("/teams/", json={"name": "", "code": "ARG"})
    assert res.status_code == 422


def test_update_team_code_case_collision(client: TestClient):
    client.post("/teams/", json={"name": "Argentina", "code": "arg"})
    bra = client.post("/teams/", json={"name": "Brasil", "code": "BRA"}).json()
    res = client.put(f"/teams/{bra['id']}", json={"code": "ARG"})
    assert res.status_code == 409


def test_update_team_code_uppercased(client: TestClient):
    res = client.post("/teams/", json={"name": "Argentina", "code": "arg"})
    team_id = res.json()["id"]
    res = client.put(f"/teams/{team_id}", json={"code": "arg2"})
    assert res.status_code == 200
    assert res.json()["code"] == "ARG2"