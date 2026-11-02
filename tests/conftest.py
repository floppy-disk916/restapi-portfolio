from src.restapi_learn2.db import async_session, engine, SQLModel, get_session, AsyncSession
from httpx import AsyncClient, ASGITransport
from collections.abc import AsyncGenerator, Callable
import pytest

from src.restapi_learn2.main import app as _app, FastAPI
from unittest import mock
from starlette import status


aiomark = pytest.mark.asyncio


@pytest.fixture()
async def test_db_session() -> AsyncGenerator[AsyncSession]:
    async with engine.begin() as conn:
        async with async_session(bind=conn) as session:
            yield session
            await session.flush()
            await session.rollback()

@pytest.fixture()
def test_session_override(test_db_session: AsyncSession) -> Callable:
    async def _test_session_override():
        yield test_db_session
    return _test_session_override

@pytest.fixture()
def app(test_session_override: Callable) -> FastAPI:
    _app.dependency_overrides[get_session] = test_session_override
    return _app

@pytest.fixture()
async def get_client(app: FastAPI) -> AsyncGenerator:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

