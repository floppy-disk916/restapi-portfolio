

from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, Depends, Security, HTTPException
from .models import *
from .auth import auth0
from .api import router as api_router
from .db import check_db_health, ASesDep, select, insert, update, delete
from datetime import datetime, UTC
from typing import Annotated


from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_db_health()
    yield


tags = [
    {
        "name": "User",
        "description": "User Operations",
    },
    {
        "name": "Item",
        "description": "Item Operations"
    },
    {
        "name": "Order",
        "description": "Order Operations",
    }
]

app = FastAPI(
    lifespan=lifespan,
    openapi_tags=tags,
    )

app.include_router(api_router)

