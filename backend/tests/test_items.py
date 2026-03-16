import pytest


@pytest.mark.asyncio
async def test_list_items_empty(client):
    resp = await client.get("/api/items")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_item(client):
    resp = await client.post("/api/items", json={"name": "Chicken Breast"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Chicken Breast"
    assert data["quantity"] == 1
    assert data["unit"] is None
    assert data["tags"] == []
    assert "id" in data


@pytest.mark.asyncio
async def test_create_item_with_tags(client):
    resp = await client.post(
        "/api/items",
        json={"name": "Ribeye", "quantity": 3, "unit": "lbs", "tags": ["freezer", "meat"]},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["quantity"] == 3
    assert data["unit"] == "lbs"
    tag_names = sorted(t["name"] for t in data["tags"])
    assert tag_names == ["freezer", "meat"]


@pytest.mark.asyncio
async def test_create_item_negative_quantity(client):
    resp = await client.post("/api/items", json={"name": "Bad", "quantity": -1})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_item_quantity(client):
    create = await client.post("/api/items", json={"name": "Steak"})
    item_id = create.json()["id"]

    resp = await client.patch(f"/api/items/{item_id}", json={"quantity": 5})
    assert resp.status_code == 200
    assert resp.json()["quantity"] == 5


@pytest.mark.asyncio
async def test_update_item_logs_quantity_change(client):
    create = await client.post("/api/items", json={"name": "Steak"})
    item_id = create.json()["id"]

    await client.patch(f"/api/items/{item_id}", json={"quantity": 5})

    resp = await client.get(f"/api/items/{item_id}/history")
    assert resp.status_code == 200
    history = resp.json()
    assert len(history) == 1
    assert history[0]["old_quantity"] == 1
    assert history[0]["new_quantity"] == 5


@pytest.mark.asyncio
async def test_update_item_not_found(client):
    resp = await client.patch("/api/items/999", json={"quantity": 5})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_item(client):
    create = await client.post("/api/items", json={"name": "Pork"})
    item_id = create.json()["id"]

    resp = await client.delete(f"/api/items/{item_id}")
    assert resp.status_code == 204

    resp = await client.get("/api/items")
    assert len(resp.json()) == 0


@pytest.mark.asyncio
async def test_delete_item_not_found(client):
    resp = await client.delete("/api/items/999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_filter_items_by_tag(client):
    await client.post("/api/items", json={"name": "Chicken", "tags": ["freezer"]})
    await client.post("/api/items", json={"name": "Rice", "tags": ["pantry"]})

    resp = await client.get("/api/items", params={"tag": "freezer"})
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["name"] == "Chicken"


@pytest.mark.asyncio
async def test_create_item_auto_creates_tags(client):
    await client.post("/api/items", json={"name": "Salmon", "tags": ["freezer", "fish"]})

    resp = await client.get("/api/tags")
    tag_names = sorted(t["name"] for t in resp.json())
    assert "fish" in tag_names
    assert "freezer" in tag_names


@pytest.mark.asyncio
async def test_tag_matching_case_insensitive(client):
    await client.post("/api/items", json={"name": "A", "tags": ["Freezer"]})
    await client.post("/api/items", json={"name": "B", "tags": ["freezer"]})

    resp = await client.get("/api/tags")
    freezer_tags = [t for t in resp.json() if t["name"].lower() == "freezer"]
    assert len(freezer_tags) == 1
