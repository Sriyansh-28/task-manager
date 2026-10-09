"""API tests. mongomock stands in for MongoDB, so no database server is needed."""
import mongomock
import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app(db=mongomock.MongoClient()["test"])
    app.config["TESTING"] = True
    return app.test_client()


def add_task(client, title="Write tests"):
    return client.post("/api/tasks", json={"title": title})


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_list_is_empty_initially(client):
    res = client.get("/api/tasks")
    assert res.status_code == 200
    assert res.get_json() == []


def test_create_task(client):
    res = add_task(client, "  Buy milk  ")
    assert res.status_code == 201
    task = res.get_json()
    assert task["title"] == "Buy milk"
    assert task["completed"] is False
    assert task["id"] and task["created_at"]

    tasks = client.get("/api/tasks").get_json()
    assert [t["id"] for t in tasks] == [task["id"]]


@pytest.mark.parametrize(
    "payload", [{}, {"title": ""}, {"title": "   "}, {"title": 123}, {"title": "x" * 201}]
)
def test_create_task_rejects_invalid_title(client, payload):
    res = client.post("/api/tasks", json=payload)
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_create_task_rejects_non_json_body(client):
    res = client.post("/api/tasks", data="not json", content_type="text/plain")
    assert res.status_code == 400


def test_complete_task(client):
    task_id = add_task(client).get_json()["id"]

    res = client.patch(f"/api/tasks/{task_id}", json={"completed": True})
    assert res.status_code == 200
    assert res.get_json()["completed"] is True
    assert client.get("/api/tasks").get_json()[0]["completed"] is True


def test_update_rejects_non_boolean(client):
    task_id = add_task(client).get_json()["id"]
    res = client.patch(f"/api/tasks/{task_id}", json={"completed": "yes"})
    assert res.status_code == 400


def test_delete_task(client):
    task_id = add_task(client).get_json()["id"]

    assert client.delete(f"/api/tasks/{task_id}").status_code == 204
    assert client.get("/api/tasks").get_json() == []
    assert client.delete(f"/api/tasks/{task_id}").status_code == 404


def test_invalid_id_returns_400(client):
    assert client.patch("/api/tasks/not-an-id", json={"completed": True}).status_code == 400
    assert client.delete("/api/tasks/not-an-id").status_code == 400


def test_missing_task_returns_404(client):
    missing = "0123456789abcdef01234567"
    assert client.patch(f"/api/tasks/{missing}", json={"completed": True}).status_code == 404
    assert client.delete(f"/api/tasks/{missing}").status_code == 404


def test_unknown_route_returns_json_404(client):
    res = client.get("/api/nope")
    assert res.status_code == 404
    assert "error" in res.get_json()
