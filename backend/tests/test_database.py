import pytest
import aiosqlite

from backend.database import init_db, get_db_path


@pytest.mark.asyncio
async def test_init_db_creates_tables(tmp_path):
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)

    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in await cursor.fetchall()]

    assert "items" in tables
    assert "tags" in tables
    assert "item_tags" in tables
    assert "quantity_log" in tables


@pytest.mark.asyncio
async def test_items_table_schema(tmp_path):
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)

    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute("PRAGMA table_info(items)")
        columns = {row[1]: row[2] for row in await cursor.fetchall()}

    assert columns["id"] == "INTEGER"
    assert columns["name"] == "TEXT"
    assert columns["quantity"] == "REAL"
    assert columns["unit"] == "TEXT"
    assert columns["barcode"] == "TEXT"
    assert columns["created_at"] == "TIMESTAMP"
    assert columns["updated_at"] == "TIMESTAMP"


@pytest.mark.asyncio
async def test_foreign_key_cascade(tmp_path):
    """Deleting an item should cascade to item_tags and quantity_log."""
    db_path = str(tmp_path / "test.db")
    await init_db(db_path)

    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute(
            "INSERT INTO items (name, quantity, created_at, updated_at) VALUES ('Test', 1, datetime('now'), datetime('now'))"
        )
        await db.execute("INSERT INTO tags (name) VALUES ('freezer')")
        await db.execute("INSERT INTO item_tags (item_id, tag_id) VALUES (1, 1)")
        await db.execute(
            "INSERT INTO quantity_log (item_id, old_quantity, new_quantity, changed_at) VALUES (1, 0, 1, datetime('now'))"
        )
        await db.commit()

        await db.execute("DELETE FROM items WHERE id = 1")
        await db.commit()

        cursor = await db.execute("SELECT COUNT(*) FROM item_tags")
        assert (await cursor.fetchone())[0] == 0

        cursor = await db.execute("SELECT COUNT(*) FROM quantity_log")
        assert (await cursor.fetchone())[0] == 0
