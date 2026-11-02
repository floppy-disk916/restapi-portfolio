

from sqlalchemy import select, insert, update, delete, text, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from .config import DATABASE_URL
from .models import SQLModel
from collections.abc import AsyncGenerator
from typing import Annotated
from fastapi import Depends, HTTPException

import logging
logger = logging.getLogger(__name__)


engine = create_async_engine(
        DATABASE_URL,
        pool_size=20,
        max_overflow=0,
        pool_recycle=3600,
        pool_pre_ping=True,
)

@event.listens_for(engine.sync_engine, "connect")
def on_connect(dbapi_con, connection_record):
    logger.info(connection_record.info)
    logger.info(connection_record.record_info)

@event.listens_for(engine.sync_engine, "checkout")
def on_checkout(dbapi_con, connection_record, connection_proxy):
    logger.info(connection_record.info)
    logger.info(connection_record.record_info)

async_session = async_sessionmaker(engine)

async def check_db_health():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.info(e)
        raise HTTPException(status_code=500, detail="DATABASE IS NOT CONNECTED")

async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        yield session
        await session.commit()

ASesDep = Annotated[AsyncSession, Depends(get_session)]
