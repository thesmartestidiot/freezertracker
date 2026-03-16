import pytest


@pytest.mark.asyncio
async def test_list_tags_empty(client):
    resp = await client.get("/api/tags")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_tag(client):
    resp = await client.post("/api/tags", json={"name": "freezer", "color": "#3b82f6"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "freezer"
    assert data["color"] == "#3b82f6"


@pytest.mark.asyncio
async def test_create_duplicate_tag(client):
    await client.post("/api/tags", json={"name": "freezer"})
    resp = await client.post("/api/tags", json={"name": "freezer"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_delete_tag(client):
    create = await client.post("/api/tags", json={"name": "meat"})
    tag_id = create.json()["id"]

    resp = await client.delete(f"/api/tags/{tag_id}")
    assert resp.status_code == 204

    resp = await client.get("/api/tags")
    assert len(resp.json()) == 0


@pytest.mark.asyncio
async def test_delete_tag_not_found(client):
    resp = await client.delete("/api/tags/999")
    assert resp.status_code == 404
