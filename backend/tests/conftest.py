# pytest-asyncio is configured in pyproject.toml (asyncio_mode = "auto")
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.database import init_db, set_db_path


@pytest_asyncio.fixture
async def client(tmp_path):
    db_path = str(tmp_path / "test.db")
    set_db_path(db_path)
    await init_db(db_path)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
