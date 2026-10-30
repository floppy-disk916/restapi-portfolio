
from .main import app
from sqlalchemy.exc import IntegrityError


@app.exception_handler(IntegrityError)
async def handle_integrity(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={"msg": "Some data already exists"},
    )

