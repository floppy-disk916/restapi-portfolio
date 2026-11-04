
from .main import app
from sqlalchemy.exc import IntegrityError

import logging

log = logging.getLogger('handlers_log')


@app.exception_handler(IntegrityError)
async def handle_integrity(request: Request, exc: IntegrityError):
    log.debug(str(exc))
    return JSONResponse(
        status_code=409,
        content={"msg": "Some data already exists"},
    )

"""
@app.exception_handler(BaseException)
async def handle_generic(request: Request, exc: BaseException):
    log.info(str(exc))
    return JSONResponse(
        status_code=500,
        content={"msg": "Generic internal errors"},
    )
"""
