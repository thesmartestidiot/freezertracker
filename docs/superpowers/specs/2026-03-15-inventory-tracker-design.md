# Freezer Tracker — Inventory Tracker Design

## Overview

A household inventory tracker for food items, starting with a chest freezer and expanding to pantry storage. The app runs on a Raspberry Pi, served over the local network, with a wall-mounted tablet as the primary interface. Any device on the LAN can access it.

## Architecture

### Stack

- **Frontend:** Vue 3 + TypeScript + Tailwind CSS (existing)
- **Backend:** FastAPI (Python) + SQLite
- **Deployment:** nginx serves the built Vue SPA as static files and reverse-proxies `/api` to FastAPI via uvicorn
- **Dev:** Vite dev server with `/api` proxy to FastAPI on localhost:8000

### Project Structure

```
freezertracker/
├── frontend/               # Vue app (relocated from root)
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.ts
│   │   ├── types.ts
│   │   ├── api.ts          # API service layer
│   │   ├── assets/
│   │   └── components/
│   │       ├── RowComp.vue
│   │       └── AddItemModal.vue
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   ├── eslint.config.ts
│   └── env.d.ts
├── backend/                # FastAPI app (new)
│   ├── main.py             # App entry, CORS, lifespan
│   ├── database.py         # SQLite connection, table creation
│   ├── models.py           # Pydantic request/response schemas
│   ├── routers/
│   │   ├── items.py        # Item CRUD endpoints
│   │   └── tags.py         # Tag endpoints
│   └── requirements.txt
└── nginx.conf              # Reference nginx config for Pi deployment
```

The existing frontend files (src/, public/, package.json, vite configs, tsconfigs, eslint config, etc.) all move into `frontend/`. The root becomes a container for the two halves plus deployment config.

## Data Model

### items

| Column     | Type           | Notes                        |
|------------|----------------|------------------------------|
| id         | INTEGER PK     | autoincrement                |
| name       | TEXT NOT NULL   | e.g., "Chicken Breast"       |
| quantity   | REAL NOT NULL   | supports decimals (2.5 lbs)  |
| unit       | TEXT NULL       | "lbs", "bags", null = count  |
| barcode    | TEXT NULL       | future UPC/barcode support   |
| created_at | TIMESTAMP      | auto on insert               |
| updated_at | TIMESTAMP      | auto on update               |

### tags

| Column | Type        | Notes                        |
|--------|-------------|------------------------------|
| id     | INTEGER PK  | autoincrement                |
| name   | TEXT UNIQUE  | e.g., "freezer", "meat"      |
| color  | TEXT NULL    | hex color for UI badges      |

### item_tags (join table)

| Column  | Type       | Notes       |
|---------|------------|-------------|
| item_id | INTEGER FK | → items.id  |
| tag_id  | INTEGER FK | → tags.id   |

Composite primary key on (item_id, tag_id).

### quantity_log

| Column       | Type       | Notes              |
|--------------|------------|--------------------|
| id           | INTEGER PK | autoincrement      |
| item_id      | INTEGER FK | → items.id         |
| old_quantity | REAL        | value before change |
| new_quantity | REAL        | value after change  |
| changed_at   | TIMESTAMP  | auto on insert     |

Every quantity mutation on an item writes a row here. This table powers future trend/usage analytics.

## API Design

All endpoints are prefixed with `/api`.

### Items

| Method   | Path              | Description                          |
|----------|-------------------|--------------------------------------|
| GET      | /api/items        | List all items with tags. Supports `?tag=` filter. |
| POST     | /api/items        | Create item. Body: `{ name, quantity, unit?, tags?: string[] }` |
| PATCH    | /api/items/{id}   | Update item fields. Quantity changes auto-log to quantity_log. |
| DELETE   | /api/items/{id}   | Delete item and its tag associations. |

### Tags

| Method   | Path              | Description                          |
|----------|-------------------|--------------------------------------|
| GET      | /api/tags         | List all tags.                       |
| POST     | /api/tags         | Create tag. Body: `{ name, color? }` |
| DELETE   | /api/tags/{id}    | Delete tag and its item associations.|

### History (future)

| Method   | Path                      | Description                  |
|----------|---------------------------|------------------------------|
| GET      | /api/items/{id}/history   | Get quantity change log.     |

### Request/Response Notes

- Tag assignment happens inline: POST/PATCH items accept a `tags` array of tag names. Unknown tag names are created automatically.
- All item responses include populated tags (name + color).
- Quantity changes via PATCH automatically log old → new in quantity_log. The client sends the desired quantity; the server handles history.

## Frontend Changes

### Types

Replace the current `Row` interface with:

```typescript
interface Tag {
  id: number
  name: string
  color: string | null
}

interface Item {
  id: number
  name: string
  quantity: number
  unit: string | null
  barcode: string | null
  tags: Tag[]
  created_at: string
  updated_at: string
}
```

### API Service Layer (`api.ts`)

A module with typed functions wrapping `fetch` calls:

- `fetchItems(tag?: string): Promise<Item[]>`
- `createItem(data: CreateItemRequest): Promise<Item>`
- `updateItem(id: number, data: UpdateItemRequest): Promise<Item>`
- `deleteItem(id: number): Promise<void>`
- `fetchTags(): Promise<Tag[]>`
- `createTag(data: CreateTagRequest): Promise<Tag>`
- `deleteTag(id: number): Promise<void>`

### Component Changes

- **App.vue:** Replace hardcoded reactive array with a `ref<Item[]>` populated by `fetchItems()` on mount. All mutations call the API then refresh or optimistically update local state.
- **RowComp.vue:** Update props from `Row` to `Item`. Display optional unit next to quantity. Show tag badges.
- **AddItemModal.vue:** Add optional unit input field and tag selector (pick existing tags or type to create new ones).
- **New: Tag filter bar** in App.vue header area — horizontal list of tag pills to filter the displayed items.

### Vite Proxy

Add to `vite.config.ts`:

```typescript
server: {
  proxy: {
    '/api': 'http://localhost:8000'
  }
}
```

## Deployment (Raspberry Pi)

- **nginx** serves `frontend/dist/` at `/` and proxies `/api` → `http://127.0.0.1:8000`
- **FastAPI** runs via `uvicorn backend.main:app` as a `systemd` service
- **SQLite** database at `/var/lib/freezertracker/db.sqlite`
- Reference `nginx.conf` included in the repo root

## Design Decisions

- **No Pinia/state management:** The item list is simple enough to manage with component state + API calls. No global store needed.
- **SQLite over Postgres:** Single-file database, zero config, easy backup (just copy the file), more than sufficient for household scale.
- **REAL for quantity:** Supports both integer counts ("3 steaks") and decimal amounts ("2.5 lbs").
- **quantity_log as append-only:** Every change is recorded, enabling trend analysis later without complicating the current item CRUD.
- **Tags over categories:** Flexible, many-to-many labeling. No rigid hierarchy to refactor when pantry support is added — just create a "pantry" tag.
- **Barcode field nullable:** Schema is ready for barcode scanning without requiring it now.
- **Tablet-first touch targets:** Existing +/- buttons are 56px (14 tailwind units), which is comfortable for touch. Maintain this minimum.

## Out of Scope (Future)

- Barcode scanning integration
- Trend analytics dashboard
- Multi-user accounts / authentication
- Shopping list generation
- Expiration date tracking
