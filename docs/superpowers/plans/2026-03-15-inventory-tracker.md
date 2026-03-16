# Inventory Tracker Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a FastAPI + SQLite backend for the freezer tracker and wire the existing Vue frontend to it, restructuring the repo into `frontend/` and `backend/` directories.

**Architecture:** FastAPI serves a REST API for item and tag CRUD with SQLite persistence. The Vue 3 + Tailwind frontend calls this API. In development, Vite proxies `/api` to FastAPI. In production, nginx serves the SPA and reverse-proxies `/api` to uvicorn.

**Tech Stack:** Python 3.11+ (FastAPI, uvicorn, aiosqlite), Vue 3, TypeScript, Tailwind CSS, Vite, SQLite, pytest

---

## File Map

### New files (backend)
- `backend/__init__.py` — empty, makes it a package
- `backend/main.py` — FastAPI app, CORS, lifespan (DB init)
- `backend/database.py` — SQLite connection helper, table creation
- `backend/models.py` — Pydantic request/response schemas
- `backend/routers/__init__.py` — empty
- `backend/routers/items.py` — item CRUD endpoints
- `backend/routers/tags.py` — tag CRUD endpoints
- `backend/requirements.txt` — Python dependencies
- `backend/tests/__init__.py` — empty
- `backend/tests/conftest.py` — pytest fixtures (test DB, test client)
- `backend/tests/test_items.py` — item endpoint tests
- `backend/tests/test_tags.py` — tag endpoint tests

### New files (frontend)
- `frontend/src/api.ts` — API service layer

### Modified files (frontend)
- `frontend/src/types.ts` — replace `Row` with `Item`, `Tag`, request types
- `frontend/src/App.vue` — API-driven state, tag filter bar, remove hardcoded data
- `frontend/src/components/RowComp.vue` — `Item` props, unit display, tag badges
- `frontend/src/components/AddItemModal.vue` — unit field, tag selector
- `frontend/src/main.ts` — remove Pinia
- `frontend/vite.config.ts` — add `/api` proxy

### New files (deployment)
- `nginx.conf` — reference nginx config

### Moved files (restructure)
- Everything currently at root (`src/`, `public/`, `index.html`, `package.json`, `vite.config.ts`, `tsconfig*.json`, `eslint.config.ts`, `env.d.ts`, `.editorconfig`, `.oxfmtrc.json`, `.oxlintrc.json`, `bun.lock`, `node_modules/`) → `frontend/`

---

## Chunk 1: Directory Restructure

### Task 1: Move frontend files into `frontend/` directory

**Files:**
- Move: all root-level frontend files into `frontend/`
- Keep at root: `.git/`, `.gitignore`, `.gitattributes`, `docs/`, `README.md`, `.vscode/`

- [ ] **Step 1: Create frontend directory and move files**

```bash
mkdir -p frontend
git mv src frontend/src
git mv public frontend/public
git mv index.html frontend/index.html
git mv package.json frontend/package.json
git mv vite.config.ts frontend/vite.config.ts
git mv tsconfig.json frontend/tsconfig.json
git mv tsconfig.app.json frontend/tsconfig.app.json
git mv tsconfig.node.json frontend/tsconfig.node.json
git mv eslint.config.ts frontend/eslint.config.ts
git mv env.d.ts frontend/env.d.ts
git mv .editorconfig frontend/.editorconfig
git mv .oxfmtrc.json frontend/.oxfmtrc.json
git mv .oxlintrc.json frontend/.oxlintrc.json
git mv bun.lock frontend/bun.lock
```

Move `node_modules` manually (not tracked by git):
```bash
mv node_modules frontend/node_modules
```

- [ ] **Step 2: Verify the frontend builds**

```bash
cd frontend && bun install && bun run build
```

Expected: build completes successfully, `frontend/dist/` is created.

- [ ] **Step 3: Verify dev server starts**

```bash
cd frontend && bun run dev
```

Expected: Vite dev server starts on port 5173. Ctrl+C to stop.

- [ ] **Step 4: Commit the restructure**

```bash
git add -A
git commit -m "chore: move frontend files into frontend/ directory"
```

---

## Chunk 2: Backend Foundation

### Task 2: Set up Python project and database layer

**Files:**
- Create: `backend/__init__.py`
- Create: `backend/database.py`
- Create: `backend/requirements.txt`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_database.py`

- [ ] **Step 1: Create backend directory structure and requirements.txt**

```bash
mkdir -p backend/routers backend/tests
touch backend/__init__.py backend/routers/__init__.py backend/tests/__init__.py
```

Write `backend/requirements.txt`:

```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
aiosqlite>=0.20.0
pytest>=8.0.0
pytest-asyncio>=0.24.0
httpx>=0.27.0
```

- [ ] **Step 2: Set up Python virtual environment and install dependencies**

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
```

- [ ] **Step 3: Update .gitignore for Python artifacts**

Add to `.gitignore`:

```
# Python
.venv/
__pycache__/
*.db
```

- [ ] **Step 4: Write the database test**

```python
# backend/tests/test_database.py
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
```

- [ ] **Step 5: Run tests to verify they fail**

```bash
python -m pytest backend/tests/test_database.py -v
```

Expected: FAIL — `backend.database` module does not exist.

- [ ] **Step 6: Write the database module**

```python
# backend/database.py
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
```

- [ ] **Step 7: Write the test conftest**

```python
# backend/tests/conftest.py
import pytest


@pytest.fixture
def anyio_backend():
    return "asyncio"
```

- [ ] **Step 8: Run tests to verify they pass**

```bash
python -m pytest backend/tests/test_database.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 9: Commit**

```bash
git add backend/
git commit -m "feat: add database layer with SQLite schema and tests"
```

### Task 3: Add Pydantic models

**Files:**
- Create: `backend/models.py`

- [ ] **Step 1: Write the models**

```python
# backend/models.py
from pydantic import BaseModel, field_validator


class CreateItemRequest(BaseModel):
    name: str
    quantity: float = 1
    unit: str | None = None
    tags: list[str] = []

    @field_validator("quantity")
    @classmethod
    def quantity_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("quantity must be >= 0")
        return v


class UpdateItemRequest(BaseModel):
    name: str | None = None
    quantity: float | None = None
    unit: str | None = None
    tags: list[str] | None = None

    @field_validator("quantity")
    @classmethod
    def quantity_non_negative(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("quantity must be >= 0")
        return v


class TagResponse(BaseModel):
    id: int
    name: str
    color: str | None


class ItemResponse(BaseModel):
    id: int
    name: str
    quantity: float
    unit: str | None
    barcode: str | None
    tags: list[TagResponse]
    created_at: str
    updated_at: str


class CreateTagRequest(BaseModel):
    name: str
    color: str | None = None
```

- [ ] **Step 2: Commit**

```bash
git add backend/models.py
git commit -m "feat: add Pydantic request/response models"
```

### Task 4: Add FastAPI app entry point

**Files:**
- Create: `backend/main.py`

- [ ] **Step 1: Write the app entry point**

```python
# backend/main.py
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_path = os.environ.get("DB_PATH", "freezertracker.db")
    await init_db(db_path)
    yield


app = FastAPI(title="Freezer Tracker", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 2: Verify the server starts**

```bash
DB_PATH=:memory: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Expected: server starts, `GET http://localhost:8000/api/health` returns `{"status":"ok"}`. Ctrl+C to stop.

- [ ] **Step 3: Commit**

```bash
git add backend/main.py
git commit -m "feat: add FastAPI app entry point with CORS and health check"
```

---

## Chunk 3: Item CRUD Endpoints

### Task 5: Add items router with tests

**Files:**
- Create: `backend/routers/items.py`
- Create: `backend/tests/test_items.py`
- Modify: `backend/main.py` (register router)
- Modify: `backend/tests/conftest.py` (add test client fixture)

- [ ] **Step 1: Update conftest with test client fixture**

```python
# backend/tests/conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.database import init_db, set_db_path


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def client(tmp_path):
    db_path = str(tmp_path / "test.db")
    set_db_path(db_path)
    await init_db(db_path)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
```

- [ ] **Step 2: Write the item endpoint tests**

```python
# backend/tests/test_items.py
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
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
python -m pytest backend/tests/test_items.py -v
```

Expected: FAIL — items router does not exist.

- [ ] **Step 4: Write the items router**

```python
# backend/routers/items.py
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
```

- [ ] **Step 5: Register the router in main.py**

Add to `backend/main.py` after the CORS middleware:

```python
from backend.routers.items import router as items_router

app.include_router(items_router)
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
python -m pytest backend/tests/test_items.py -v
```

Expected: all 12 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/
git commit -m "feat: add item CRUD endpoints with tests"
```

---

## Chunk 4: Tag CRUD Endpoints

### Task 6: Add tags router with tests

**Files:**
- Create: `backend/routers/tags.py`
- Create: `backend/tests/test_tags.py`
- Modify: `backend/main.py` (register router)

- [ ] **Step 1: Write the tag endpoint tests**

```python
# backend/tests/test_tags.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest backend/tests/test_tags.py -v
```

Expected: FAIL — tags router does not exist.

- [ ] **Step 3: Write the tags router**

```python
# backend/routers/tags.py
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
```

- [ ] **Step 4: Register the router in main.py**

Add to `backend/main.py`:

```python
from backend.routers.tags import router as tags_router

app.include_router(tags_router)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
python -m pytest backend/tests/test_tags.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 6: Run all backend tests**

```bash
python -m pytest backend/tests/ -v
```

Expected: all tests PASS (database + items + tags).

- [ ] **Step 7: Commit**

```bash
git add backend/
git commit -m "feat: add tag CRUD endpoints with tests"
```

---

## Chunk 5: Frontend — Types, API Layer, and Vite Proxy

### Task 7: Update TypeScript types and add API service

**Files:**
- Modify: `frontend/src/types.ts`
- Create: `frontend/src/api.ts`
- Modify: `frontend/vite.config.ts`
- Modify: `frontend/src/main.ts`

- [ ] **Step 1: Update types.ts**

```typescript
// frontend/src/types.ts
export interface Tag {
  id: number
  name: string
  color: string | null
}

export interface Item {
  id: number
  name: string
  quantity: number
  unit: string | null
  barcode: string | null
  tags: Tag[]
  created_at: string
  updated_at: string
}

export interface CreateItemRequest {
  name: string
  quantity?: number
  unit?: string | null
  tags?: string[]
}

export interface UpdateItemRequest {
  name?: string
  quantity?: number
  unit?: string | null
  tags?: string[]
}

export interface CreateTagRequest {
  name: string
  color?: string | null
}
```

- [ ] **Step 2: Create api.ts**

```typescript
// frontend/src/api.ts
import type { Item, Tag, CreateItemRequest, UpdateItemRequest, CreateTagRequest } from '@/types'

const BASE = '/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!resp.ok) {
    throw new Error(`API error: ${resp.status}`)
  }
  if (resp.status === 204) return undefined as T
  return resp.json()
}

export async function fetchItems(tag?: string | string[]): Promise<Item[]> {
  const params = new URLSearchParams()
  if (tag) {
    const tags = Array.isArray(tag) ? tag : [tag]
    tags.forEach((t) => params.append('tag', t))
  }
  const query = params.toString()
  return request<Item[]>(`/items${query ? `?${query}` : ''}`)
}

export async function createItem(data: CreateItemRequest): Promise<Item> {
  return request<Item>('/items', { method: 'POST', body: JSON.stringify(data) })
}

export async function updateItem(id: number, data: UpdateItemRequest): Promise<Item> {
  return request<Item>(`/items/${id}`, { method: 'PATCH', body: JSON.stringify(data) })
}

export async function deleteItem(id: number): Promise<void> {
  return request<void>(`/items/${id}`, { method: 'DELETE' })
}

export async function fetchTags(): Promise<Tag[]> {
  return request<Tag[]>('/tags')
}

export async function createTag(data: CreateTagRequest): Promise<Tag> {
  return request<Tag>('/tags', { method: 'POST', body: JSON.stringify(data) })
}

export async function deleteTag(id: number): Promise<void> {
  return request<void>(`/tags/${id}`, { method: 'DELETE' })
}
```

- [ ] **Step 3: Add Vite proxy config**

Replace `frontend/vite.config.ts` with:

```typescript
import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vueDevTools from "vite-plugin-vue-devtools";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [vue(), vueDevTools(), tailwindcss()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
```

- [ ] **Step 4: Remove Pinia from main.ts and package.json**

```typescript
// frontend/src/main.ts
import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
```

Then remove the dependency:

```bash
cd frontend && bun remove pinia
```

- [ ] **Step 5: Verify frontend builds**

```bash
cd frontend && bun run build
```

Expected: build succeeds.

- [ ] **Step 6: Commit**

```bash
cd frontend
git add src/types.ts src/api.ts vite.config.ts src/main.ts
git commit -m "feat: add API service layer, update types, add Vite proxy"
```

---

## Chunk 6: Frontend — Wire Components to API

### Task 8: Update App.vue to use API

**Files:**
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Rewrite App.vue**

```vue
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import RowComp from '@/components/RowComp.vue'
import AddItemModal from '@/components/AddItemModal.vue'
import type { Item, Tag } from '@/types'
import { fetchItems, fetchTags, createItem, updateItem, deleteItem } from '@/api'

const items = ref<Item[]>([])
const tags = ref<Tag[]>([])
const activeTag = ref<string | null>(null)

const sortedItems = computed(() => {
  return [...items.value].sort((a, b) => a.name.localeCompare(b.name))
})

const filteredItems = computed(() => {
  if (!activeTag.value) return sortedItems.value
  return sortedItems.value.filter((item) =>
    item.tags.some((t) => t.name.toLowerCase() === activeTag.value!.toLowerCase()),
  )
})

async function loadData() {
  const [itemData, tagData] = await Promise.all([fetchItems(), fetchTags()])
  items.value = itemData
  tags.value = tagData
}

async function handleUpdateQuantity(id: number, quantity: number) {
  await updateItem(id, { quantity: Math.max(0, quantity) })
  await loadData()
}

async function handleAddItem(name: string, unit: string | null, itemTags: string[]) {
  await createItem({ name, unit: unit || undefined, tags: itemTags })
  await loadData()
}

async function handleDeleteItem(id: number) {
  await deleteItem(id)
  await loadData()
}

function toggleTag(tagName: string) {
  activeTag.value = activeTag.value === tagName ? null : tagName
}

onMounted(loadData)
</script>

<template>
  <div class="h-screen w-screen bg-gray-900 p-4">
    <div class="mx-auto flex h-full w-full flex-col overflow-hidden rounded-lg bg-gray-800">
      <header class="flex items-center gap-4 border-b border-gray-700 p-4">
        <img src="./assets/doggo.png" alt="" class="h-14 w-14 rounded-lg object-cover" />
        <div class="flex-1">
          <h1 class="text-xl font-semibold text-white">Freezer Tracker</h1>
          <p class="text-sm text-gray-300">Manage your inventory</p>
        </div>
      </header>

      <div v-if="tags.length" class="flex gap-2 overflow-x-auto border-b border-gray-700 px-4 py-3">
        <button
          v-for="tag in tags"
          :key="tag.id"
          type="button"
          class="shrink-0 rounded-full px-3 py-1 text-sm font-medium transition"
          :class="
            activeTag === tag.name
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          "
          @click="toggleTag(tag.name)"
        >
          {{ tag.name }}
        </button>
      </div>

      <main class="min-h-0 flex-1 overflow-y-auto p-4 space-y-4">
        <RowComp
          v-for="item in filteredItems"
          :key="item.id"
          :item="item"
          @update-quantity="handleUpdateQuantity(item.id, $event)"
          @delete="handleDeleteItem(item.id)"
        />
      </main>

      <footer class="flex justify-between items-center w-full border-t border-gray-700 p-4">
        <div class="text-xl text-gray-300">{{ filteredItems.length }} items</div>
        <AddItemModal :tags="tags" @add-item="handleAddItem" />
      </footer>
    </div>
  </div>
</template>
```

- [ ] **Step 2: Commit**

```bash
cd frontend && git add src/App.vue
git commit -m "feat: wire App.vue to backend API with tag filtering"
```

### Task 9: Update RowComp.vue

**Files:**
- Modify: `frontend/src/components/RowComp.vue`

- [ ] **Step 1: Rewrite RowComp.vue**

```vue
<script setup lang="ts">
import type { Item } from '@/types'

defineProps<{ item: Item }>()
defineEmits<{
  updateQuantity: [value: number]
  delete: []
}>()
</script>

<template>
  <div
    class="flex h-16 w-full gap-4 items-center justify-between bg-gray-800 px-4 text-white rounded-lg text-3xl"
  >
    <div class="flex flex-1 items-center gap-3 overflow-hidden">
      <span class="truncate">{{ item.name }}</span>
      <span v-if="item.unit" class="text-base text-gray-400">({{ item.unit }})</span>
      <span
        v-for="tag in item.tags"
        :key="tag.id"
        class="rounded-full px-2 py-0.5 text-xs font-medium"
        :style="{ backgroundColor: tag.color || '#374151', color: '#fff' }"
      >
        {{ tag.name }}
      </span>
    </div>
    <button
      type="button"
      class="flex items-center justify-center bg-gray-700 size-14 p-2 rounded"
      @click="$emit('updateQuantity', item.quantity - 1)"
    >
      -
    </button>
    <span class="w-16 text-center">{{ item.quantity }}</span>
    <button
      type="button"
      class="flex items-center justify-center bg-gray-700 size-14 p-2 rounded"
      @click="$emit('updateQuantity', item.quantity + 1)"
    >
      +
    </button>
    <button
      v-if="item.quantity === 0"
      type="button"
      class="flex items-center justify-center bg-red-700 size-14 p-2 rounded text-lg"
      @click="$emit('delete')"
    >
      &times;
    </button>
  </div>
</template>
```

- [ ] **Step 2: Commit**

```bash
cd frontend && git add src/components/RowComp.vue
git commit -m "feat: update RowComp to display Item with unit and tag badges"
```

### Task 10: Update AddItemModal.vue

**Files:**
- Modify: `frontend/src/components/AddItemModal.vue`

- [ ] **Step 1: Rewrite AddItemModal.vue**

```vue
<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import type { Tag } from '@/types'

const props = defineProps<{ tags: Tag[] }>()

const emit = defineEmits<{
  addItem: [name: string, unit: string | null, tags: string[]]
}>()

const isOpen = ref(false)
const newItemName = ref('')
const newItemUnit = ref('')
const tagInput = ref('')
const selectedTags = ref<string[]>([])
const inputRef = ref<HTMLInputElement | null>(null)

const canSubmit = computed(() => newItemName.value.trim().length > 0)

const filteredSuggestions = computed(() => {
  if (!tagInput.value.trim()) return []
  const query = tagInput.value.toLowerCase()
  return props.tags
    .filter(
      (t) =>
        t.name.toLowerCase().includes(query) &&
        !selectedTags.value.includes(t.name),
    )
    .slice(0, 5)
})

function openModal() {
  isOpen.value = true
}

function closeModal() {
  isOpen.value = false
  newItemName.value = ''
  newItemUnit.value = ''
  tagInput.value = ''
  selectedTags.value = []
}

function submitItem() {
  const name = newItemName.value.trim()
  if (name) {
    const unit = newItemUnit.value.trim() || null
    emit('addItem', name, unit, [...selectedTags.value])
    closeModal()
  }
}

function addTag(tagName: string) {
  const name = tagName.trim()
  if (name && !selectedTags.value.includes(name)) {
    selectedTags.value.push(name)
  }
  tagInput.value = ''
}

function removeTag(tagName: string) {
  selectedTags.value = selectedTags.value.filter((t) => t !== tagName)
}

function handleTagKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    e.preventDefault()
    if (tagInput.value.trim()) {
      addTag(tagInput.value)
    }
  }
}

watch(isOpen, async (open) => {
  if (typeof document !== 'undefined') {
    document.body.style.overflow = open ? 'hidden' : ''
  }
  if (open) {
    await nextTick()
    inputRef.value?.focus()
  }
})

onBeforeUnmount(() => {
  if (typeof document !== 'undefined') {
    document.body.style.overflow = ''
  }
})
</script>

<template>
  <div class="inline-flex">
    <button
      type="button"
      class="rounded bg-blue-600 px-4 py-2 font-medium text-white transition hover:bg-blue-500"
      @click="openModal"
    >
      Add Item
    </button>
  </div>

  <Teleport to="body">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
      @click.self="closeModal"
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Add new item"
        class="w-full max-w-md rounded-lg border border-gray-700 bg-gray-800 p-6 text-white shadow-2xl"
        @keydown.esc="closeModal"
      >
        <h2 class="mb-4 text-xl font-semibold">Add New Item</h2>

        <label for="new-item-name" class="mb-2 block text-sm text-gray-300">Item name</label>
        <input
          id="new-item-name"
          ref="inputRef"
          v-model="newItemName"
          type="text"
          placeholder="ex: Ground beef"
          class="mb-4 w-full rounded border border-gray-600 bg-gray-900 px-3 py-2 text-white outline-none transition focus:border-blue-500"
          @keydown.enter.prevent="submitItem"
        />

        <label for="new-item-unit" class="mb-2 block text-sm text-gray-300">Unit (optional)</label>
        <input
          id="new-item-unit"
          v-model="newItemUnit"
          type="text"
          placeholder="ex: lbs, bags, packs"
          class="mb-4 w-full rounded border border-gray-600 bg-gray-900 px-3 py-2 text-white outline-none transition focus:border-blue-500"
        />

        <label class="mb-2 block text-sm text-gray-300">Tags</label>
        <div class="mb-2 flex flex-wrap gap-2">
          <span
            v-for="tag in selectedTags"
            :key="tag"
            class="flex items-center gap-1 rounded-full bg-blue-600 px-3 py-1 text-sm"
          >
            {{ tag }}
            <button type="button" class="ml-1 text-blue-200 hover:text-white" @click="removeTag(tag)">
              &times;
            </button>
          </span>
        </div>
        <div class="relative mb-5">
          <input
            v-model="tagInput"
            type="text"
            placeholder="Type to add tags..."
            class="w-full rounded border border-gray-600 bg-gray-900 px-3 py-2 text-white outline-none transition focus:border-blue-500"
            @keydown="handleTagKeydown"
          />
          <div
            v-if="filteredSuggestions.length"
            class="absolute z-10 mt-1 w-full rounded border border-gray-600 bg-gray-900 shadow-lg"
          >
            <button
              v-for="suggestion in filteredSuggestions"
              :key="suggestion.id"
              type="button"
              class="block w-full px-3 py-2 text-left text-sm text-gray-200 hover:bg-gray-700"
              @click="addTag(suggestion.name)"
            >
              {{ suggestion.name }}
            </button>
          </div>
        </div>

        <div class="flex justify-end gap-3">
          <button
            type="button"
            class="rounded border border-gray-600 px-4 py-2 text-gray-200 transition hover:bg-gray-700"
            @click="closeModal"
          >
            Cancel
          </button>
          <button
            type="button"
            class="rounded bg-blue-600 px-4 py-2 font-medium text-white transition enabled:hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="!canSubmit"
            @click="submitItem"
          >
            Add
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
```

- [ ] **Step 2: Commit**

```bash
cd frontend && git add src/components/AddItemModal.vue
git commit -m "feat: update AddItemModal with unit and tag inputs"
```

---

## Chunk 7: Deployment Config and Cleanup

### Task 11: Add nginx reference config

**Files:**
- Create: `nginx.conf`

- [ ] **Step 1: Write the nginx config**

```nginx
# nginx.conf — reference config for Raspberry Pi deployment
# Copy to /etc/nginx/sites-available/freezertracker and symlink to sites-enabled

server {
    listen 80;
    server_name _;

    # Serve Vue SPA
    root /opt/freezertracker/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API to FastAPI
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add nginx.conf
git commit -m "docs: add reference nginx config for Pi deployment"
```

### Task 12: Verify full stack end-to-end

- [ ] **Step 1: Start the backend**

```bash
source backend/.venv/bin/activate && DB_PATH=freezertracker.db python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

- [ ] **Step 2: Start the frontend (separate terminal)**

```bash
cd frontend && bun run dev
```

- [ ] **Step 3: Manual smoke test**

Open `http://localhost:5173` in a browser. Verify:
1. Empty item list loads
2. Click "Add Item" → enter name, optional unit, optional tags → item appears
3. Click +/- → quantity updates
4. Tag pills appear in the header when tags exist
5. Clicking a tag pill filters the list

- [ ] **Step 4: Run all backend tests one final time**

```bash
python -m pytest backend/tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 5: Build frontend for production**

```bash
cd frontend && bun run build
```

Expected: build succeeds.

- [ ] **Step 6: Final commit if any cleanup needed**

```bash
git status
```
