"""API unit tests."""
from fastapi.testclient import TestClient

def _create(client, **kwargs):
    payload = {"title": "Test todo", "description": "", "priority": "medium"}
    payload.update(kwargs)
    return client.post("/api/todos", json=payload)


# ---- CRUD lifecycle ----
def test_create_todo(client: TestClient):
    resp = _create(client, title="Buy milk", description="2 liters", priority="high")
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == 1
    assert data["title"] == "Buy milk"
    assert data["description"] == "2 liters"
    assert data["priority"] == "high"
    assert data["completed"] is False
    assert data["created_at"] is not None


def test_list_todos(client: TestClient):
    _create(client, title="A")
    _create(client, title="B")
    resp = client.get("/api/todos")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_todo(client: TestClient):
    _create(client, title="Find me")
    resp = client.get("/api/todos/1")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Find me"


def test_get_todo_not_found(client: TestClient):
    resp = client.get("/api/todos/999")
    assert resp.status_code == 404


def test_update_todo(client: TestClient):
    _create(client, title="Old")
    resp = client.patch("/api/todos/1", json={"title": "New", "completed": True})
    assert resp.status_code == 200
    assert resp.json()["title"] == "New"
    assert resp.json()["completed"] is True


def test_update_todo_partial(client: TestClient):
    _create(client, title="Keep", description="original", priority="low")
    resp = client.patch("/api/todos/1", json={"completed": True})
    assert resp.json()["completed"] is True
    assert resp.json()["title"] == "Keep"  # unchanged
    assert resp.json()["description"] == "original"


def test_update_todo_not_found(client: TestClient):
    resp = client.patch("/api/todos/999", json={"title": "X"})
    assert resp.status_code == 404


def test_toggle_todo(client: TestClient):
    _create(client, title="Toggle me")
    r1 = client.post("/api/todos/1/toggle")
    assert r1.json()["completed"] is True
    r2 = client.post("/api/todos/1/toggle")
    assert r2.json()["completed"] is False


def test_delete_todo(client: TestClient):
    _create(client, title="Delete me")
    resp = client.delete("/api/todos/1")
    assert resp.status_code == 204
    assert client.get("/api/todos/1").status_code == 404


def test_delete_todo_not_found(client: TestClient):
    resp = client.delete("/api/todos/999")
    assert resp.status_code == 404


# ---- Filtering & sorting ----
def test_filter_by_completed(client: TestClient):
    _create(client, title="Done")
    _create(client, title="Not done")
    client.post("/api/todos/1/toggle")
    resp = client.get("/api/todos?completed=true")
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "Done"
    resp = client.get("/api/todos?completed=false")
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "Not done"


def test_filter_by_priority(client: TestClient):
    _create(client, title="Low", priority="low")
    _create(client, title="High", priority="high")
    resp = client.get("/api/todos?priority=high")
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "High"


def test_search(client: TestClient):
    _create(client, title="Buy groceries", description="milk")
    _create(client, title="Walk dog", description="in the park")
    resp = client.get("/api/todos?search=groceries")
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "Buy groceries"
    resp = client.get("/api/todos?search=park")
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "Walk dog"


def test_sort_by_title(client: TestClient):
    _create(client, title="Cherry")
    _create(client, title="Apple")
    _create(client, title="Banana")
    resp = client.get("/api/todos?sort=title_asc")
    titles = [t["title"] for t in resp.json()]
    assert titles == ["Apple", "Banana", "Cherry"]


# ---- Stats ----
def test_stats(client: TestClient):
    _create(client, title="A", priority="high")
    _create(client, title="B", priority="low")
    _create(client, title="C", priority="high")
    client.post("/api/todos/1/toggle")
    resp = client.get("/api/todos/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert data["completed"] == 1
    assert data["active"] == 2
    assert data["by_priority"]["high"] == 2
    assert data["by_priority"]["low"] == 1


# ---- Clear completed ----
def test_clear_completed(client: TestClient):
    _create(client, title="Done 1")
    _create(client, title="Done 2")
    _create(client, title="Active")
    client.post("/api/todos/1/toggle")
    client.post("/api/todos/2/toggle")
    resp = client.delete("/api/todos")
    assert resp.status_code == 200
    assert resp.json()["cleared"] == 2
    remaining = client.get("/api/todos").json()
    assert len(remaining) == 1
    assert remaining[0]["title"] == "Active"


# ---- Validation ----
def test_invalid_priority(client: TestClient):
    resp = _create(client, priority="urgent")
    assert resp.status_code == 422


def test_empty_title_rejected(client: TestClient):
    resp = client.post("/api/todos", json={"title": "", "priority": "low"})
    assert resp.status_code == 422


def test_missing_title_rejected(client: TestClient):
    resp = client.post("/api/todos", json={"priority": "low"})
    assert resp.status_code == 422


# ---- Health ----
def test_health(client: TestClient):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
