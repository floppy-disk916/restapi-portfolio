import redis.asyncio as redis
from .config import REDIS_URL
from typing import Any
from contextlib import asynccontextmanager

cache_pool = redis.ConnectionPool.from_url(REDIS_URL)

@asynccontextmanager
async def get_redis() -> redis.Redis:
    red = await redis.Redis(connection_pool = cache_pool)
    try:
        yield red
    finally:
        await red.aclose()


TTL_sec = 120

async def set_to_cache(tag: str, data: str):
    async with get_redis() as red:
        await red.set(tag, data, ex=TTL_sec)

async def get_from_cache(tag: str) -> str | None:
    async with get_redis() as red:
        return await red.get(tag)

async def inval_cache(tag: str):
    async with get_redis() as red:
        await red.delete(tag)
