import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(autouse=True)
def clear_items():
    """Reset in-memory store before each test."""
    import app.main as main_module

    main_module.items.clear()
    main_module._next_id = 1
    yield
    main_module.items.clear()
    main_module._next_id = 1


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_item():
    return {"name": "Widget", "description": "A test widget", "price": 9.99, "in_stock": True}


# --- Root & Health ---


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- List Items ---


def test_list_items_empty(client):
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []


def test_list_items_with_data(client, sample_item):
    client.post("/items", json=sample_item)
    client.post("/items", json={**sample_item, "name": "Gadget"})
    response = client.get("/items")
    assert response.status_code == 200
    assert len(response.json()) == 2


# --- Create Item ---


def test_create_item(client, sample_item):
    response = client.post("/items", json=sample_item)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Widget"
    assert data["price"] == 9.99


def test_create_item_missing_name(client):
    response = client.post("/items", json={"price": 5.0})
    assert response.status_code == 422


def test_create_item_invalid_price(client):
    response = client.post("/items", json={"name": "Bad", "price": "not-a-number"})
    assert response.status_code == 422


def test_create_item_increments_id(client, sample_item):
    r1 = client.post("/items", json=sample_item)
    r2 = client.post("/items", json={**sample_item, "name": "Second"})
    assert r1.json()["id"] == 1
    assert r2.json()["id"] == 2


# --- Get Item ---


def test_get_item(client, sample_item):
    client.post("/items", json=sample_item)
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Widget"


def test_get_item_not_found(client):
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


# --- Update Item ---


def test_update_item(client, sample_item):
    client.post("/items", json=sample_item)
    updated = {**sample_item, "name": "Updated Widget", "price": 19.99}
    response = client.put("/items/1", json=updated)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Widget"
    assert response.json()["price"] == 19.99


def test_update_item_not_found(client, sample_item):
    response = client.put("/items/999", json=sample_item)
    assert response.status_code == 404


# --- Delete Item ---


def test_delete_item(client, sample_item):
    client.post("/items", json=sample_item)
    response = client.delete("/items/1")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"]


def test_delete_item_not_found(client):
    response = client.delete("/items/999")
    assert response.status_code == 404


def test_delete_removes_item(client, sample_item):
    client.post("/items", json=sample_item)
    client.delete("/items/1")
    response = client.get("/items/1")
    assert response.status_code == 404
