import aiosqlite

_db_path: str = "freezertracker.db"


def get_db_path() -> str:
    return _db_path


def set_db_path(path: str) -> None:
    global _db_path
    _db_path = path


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(_db_path)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA foreign_keys = ON")
    return db


async def init_db(db_path: str | None = None) -> None:
    if db_path is not None:
        set_db_path(db_path)

    async with aiosqlite.connect(_db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity REAL NOT NULL DEFAULT 1,
                unit TEXT,
                barcode TEXT,
                created_at TIMESTAMP DEFAULT (datetime('now')),
                updated_at TIMESTAMP DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL COLLATE NOCASE,
                color TEXT
            );

            CREATE TABLE IF NOT EXISTS item_tags (
                item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
                tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
                PRIMARY KEY (item_id, tag_id)
            );

            CREATE TABLE IF NOT EXISTS quantity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
                old_quantity REAL NOT NULL,
                new_quantity REAL NOT NULL,
                changed_at TIMESTAMP DEFAULT (datetime('now'))
            );
        """)
        await db.commit()
