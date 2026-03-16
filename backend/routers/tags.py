from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from backend.database import get_db
from backend.models import CreateTagRequest, TagResponse

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=list[TagResponse])
async def list_tags():
    db = await get_db()
    try:
        cursor = await db.execute("SELECT id, name, color FROM tags ORDER BY name")
        rows = await cursor.fetchall()
        return [TagResponse(id=r["id"], name=r["name"], color=r["color"]) for r in rows]
    finally:
        await db.close()


@router.post("", response_model=TagResponse, status_code=HTTP_201_CREATED)
async def create_tag(req: CreateTagRequest):
    db = await get_db()
    try:
        cursor = await db.execute("SELECT id FROM tags WHERE name = ? COLLATE NOCASE", (req.name,))
        if await cursor.fetchone():
            raise HTTPException(status_code=409, detail="Tag already exists")

        cursor = await db.execute(
            "INSERT INTO tags (name, color) VALUES (?, ?)", (req.name, req.color)
        )
        tag_id = cursor.lastrowid
        await db.commit()
        return TagResponse(id=tag_id, name=req.name, color=req.color)
    finally:
        await db.close()


@router.delete("/{tag_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int):
    db = await get_db()
    try:
        cursor = await db.execute("SELECT id FROM tags WHERE id = ?", (tag_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="Tag not found")
        await db.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        await db.commit()
    finally:
        await db.close()
