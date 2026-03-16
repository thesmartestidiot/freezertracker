from fastapi import APIRouter, HTTPException, Query
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from backend.database import get_db
from backend.models import CreateItemRequest, UpdateItemRequest, ItemResponse, TagResponse

router = APIRouter(prefix="/api/items", tags=["items"])


async def _get_tags_for_item(db, item_id: int) -> list[TagResponse]:
    cursor = await db.execute(
        """
        SELECT t.id, t.name, t.color
        FROM tags t
        JOIN item_tags it ON it.tag_id = t.id
        WHERE it.item_id = ?
        ORDER BY t.name
        """,
        (item_id,),
    )
    rows = await cursor.fetchall()
    return [TagResponse(id=r["id"], name=r["name"], color=r["color"]) for r in rows]


async def _resolve_tag_ids(db, tag_names: list[str]) -> list[int]:
    tag_ids = []
    for name in tag_names:
        cursor = await db.execute("SELECT id FROM tags WHERE name = ? COLLATE NOCASE", (name,))
        row = await cursor.fetchone()
        if row:
            tag_ids.append(row["id"])
        else:
            cursor = await db.execute("INSERT INTO tags (name) VALUES (?)", (name,))
            tag_ids.append(cursor.lastrowid)
    await db.commit()
    return tag_ids


async def _set_item_tags(db, item_id: int, tag_ids: list[int]) -> None:
    await db.execute("DELETE FROM item_tags WHERE item_id = ?", (item_id,))
    for tag_id in tag_ids:
        await db.execute("INSERT INTO item_tags (item_id, tag_id) VALUES (?, ?)", (item_id, tag_id))
    await db.commit()


async def _build_item_response(db, item_id: int) -> ItemResponse:
    cursor = await db.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    item = await cursor.fetchone()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    tags = await _get_tags_for_item(db, item_id)
    return ItemResponse(
        id=item["id"],
        name=item["name"],
        quantity=item["quantity"],
        unit=item["unit"],
        barcode=item["barcode"],
        tags=tags,
        created_at=item["created_at"],
        updated_at=item["updated_at"],
    )


@router.get("", response_model=list[ItemResponse])
async def list_items(tag: list[str] = Query(default=[])):
    db = await get_db()
    try:
        if tag:
            placeholders = ",".join("?" for _ in tag)
            cursor = await db.execute(
                f"""
                SELECT DISTINCT i.id FROM items i
                JOIN item_tags it ON it.item_id = i.id
                JOIN tags t ON t.id = it.tag_id
                WHERE t.name COLLATE NOCASE IN ({placeholders})
                GROUP BY i.id
                HAVING COUNT(DISTINCT t.id) = ?
                """,
                (*tag, len(tag)),
            )
            rows = await cursor.fetchall()
            item_ids = [r["id"] for r in rows]
            if not item_ids:
                return []
            return [await _build_item_response(db, iid) for iid in item_ids]
        else:
            cursor = await db.execute("SELECT id FROM items ORDER BY id")
            rows = await cursor.fetchall()
            return [await _build_item_response(db, r["id"]) for r in rows]
    finally:
        await db.close()


@router.post("", response_model=ItemResponse, status_code=HTTP_201_CREATED)
async def create_item(req: CreateItemRequest):
    db = await get_db()
    try:
        cursor = await db.execute(
            "INSERT INTO items (name, quantity, unit) VALUES (?, ?, ?)",
            (req.name, req.quantity, req.unit),
        )
        item_id = cursor.lastrowid
        await db.commit()

        if req.tags:
            tag_ids = await _resolve_tag_ids(db, req.tags)
            await _set_item_tags(db, item_id, tag_ids)

        return await _build_item_response(db, item_id)
    finally:
        await db.close()


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, req: UpdateItemRequest):
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        existing = await cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Item not found")

        if req.quantity is not None and req.quantity != existing["quantity"]:
            await db.execute(
                "INSERT INTO quantity_log (item_id, old_quantity, new_quantity) VALUES (?, ?, ?)",
                (item_id, existing["quantity"], req.quantity),
            )

        updates = {}
        if req.name is not None:
            updates["name"] = req.name
        if req.quantity is not None:
            updates["quantity"] = req.quantity
        if req.unit is not None:
            updates["unit"] = req.unit

        if updates:
            set_clause = ", ".join(f"{k} = ?" for k in updates)
            values = list(updates.values())
            await db.execute(
                f"UPDATE items SET {set_clause}, updated_at = datetime('now') WHERE id = ?",
                (*values, item_id),
            )
            await db.commit()

        if req.tags is not None:
            tag_ids = await _resolve_tag_ids(db, req.tags)
            await _set_item_tags(db, item_id, tag_ids)

        return await _build_item_response(db, item_id)
    finally:
        await db.close()


@router.delete("/{item_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    db = await get_db()
    try:
        cursor = await db.execute("SELECT id FROM items WHERE id = ?", (item_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="Item not found")
        await db.execute("DELETE FROM items WHERE id = ?", (item_id,))
        await db.commit()
    finally:
        await db.close()


@router.get("/{item_id}/history")
async def get_item_history(item_id: int):
    db = await get_db()
    try:
        cursor = await db.execute("SELECT id FROM items WHERE id = ?", (item_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="Item not found")
        cursor = await db.execute(
            "SELECT old_quantity, new_quantity, changed_at FROM quantity_log WHERE item_id = ? ORDER BY changed_at",
            (item_id,),
        )
        rows = await cursor.fetchall()
        return [
            {"old_quantity": r["old_quantity"], "new_quantity": r["new_quantity"], "changed_at": r["changed_at"]}
            for r in rows
        ]
    finally:
        await db.close()
