
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, Depends, Security, HTTPException
from .models import *
from .api import router as api_router
from .db import check_db_health, ASesDep, select, insert, update, delete
from datetime import datetime, UTC
from typing import Annotated

import logging
from sqlalchemy.exc import (
    InvalidRequestError,
    DatabaseError,
    DataError,
    IntegrityError,
    MissingGreenlet,
)

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

log = logging.getLogger('handler_log')


import sys

@app.exception_handler(MissingGreenlet)
async def handle_greenlet_error(request: Request, exc: MissingGreenlet):
    log.info(str(exc))
    log.info("EXITING============================\n\n\n")
    sys.exit()

@app.exception_handler(IntegrityError)
async def handle_integrity(request: Request, exc: IntegrityError):
    log.info(str(exc))
    return JSONResponse(
        status_code=409,
        content={"msg": "Already exists"},
    )

@app.exception_handler(InvalidRequestError)
async def handle_bad_request(request: Request, exc: InvalidRequestError):
    log.info(str(exc))
    return JSONResponse(
        status_code=400
    )

@app.exception_handler(DatabaseError)
async def handle_database_error(request: Request, exc: DatabaseError):
    import pdb; pdb.set_trace()
    log.info(str(exc))
    return JSONResponse(
        status_code=500,
        content={"msg": "Database Error"},
    )

@app.exception_handler(Exception)
async def handle_generic(request: Request, exc: Exception):
    log.info(str(exc))
    return JSONResponse(
        status_code=500,
        content={"msg": "Generic internal errors"},
    )
