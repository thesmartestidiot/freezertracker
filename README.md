# Freezer Tracker

A household inventory tracker for freezer contents. Built with a Vue 3 frontend and Python FastAPI backend, designed for use on a wall-mounted tablet (Raspberry Pi).

## Features

- Add items with name, quantity, optional unit (lbs, bags, etc.), and tags
- Increment/decrement quantities with large, touch-friendly buttons
- Tag items with colored labels and filter the list by tag
- Quantity change history logging

## Tech Stack

- **Frontend:** Vue 3, TypeScript, Tailwind CSS, Vite
- **Backend:** Python 3.14+, FastAPI, aiosqlite (SQLite)
- **Deployment:** Nginx + Uvicorn on Raspberry Pi

## Project Structure

```
freezertracker/
├── backend/
│   ├── main.py            # FastAPI app, CORS, lifespan
│   ├── database.py        # SQLite schema & connection
│   ├── models.py          # Pydantic schemas
│   ├── routers/
│   │   ├── items.py       # Item CRUD + history
│   │   └── tags.py        # Tag CRUD
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── App.vue        # Main app component
│   │   ├── api.ts         # API service layer
│   │   ├── types.ts       # TypeScript interfaces
│   │   └── components/
│   │       ├── RowComp.vue
│   │       └── AddItemModal.vue
│   └── vite.config.ts
├── nginx.conf             # Reference deployment config
└── docs/
```

## Development

### Prerequisites

- Python 3.14+
- [Bun](https://bun.sh/)

### Backend

```sh
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs at `http://localhost:8000`.

### Frontend

```sh
cd frontend
bun install
bun dev
```

The dev server runs at `http://localhost:5173` and proxies `/api` requests to the backend.

### Tests

```sh
cd backend
pytest
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/items` | List items (optional `?tag=` filter) |
| POST | `/api/items` | Create item |
| PATCH | `/api/items/{id}` | Update item |
| DELETE | `/api/items/{id}` | Delete item |
| GET | `/api/items/{id}/history` | Quantity change log |
| GET | `/api/tags` | List tags |
| POST | `/api/tags` | Create tag |
| DELETE | `/api/tags/{id}` | Delete tag |
| GET | `/api/health` | Health check |

## Deployment

The app is designed to run on a Raspberry Pi with nginx serving the built frontend and proxying API requests to uvicorn. See `nginx.conf` for the reference configuration.

```sh
# Build frontend
cd frontend && bun run build

# Run backend
cd backend && uvicorn main:app --host 0.0.0.0
```

The database is a SQLite file (configurable via `DB_PATH` env var, defaults to `freezertracker.db`).
