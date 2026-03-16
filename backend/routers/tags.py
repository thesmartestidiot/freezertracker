from fastapi import APIRouter

from backend.database import get_db
from backend.models import TagResponse

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
