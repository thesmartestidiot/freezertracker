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
