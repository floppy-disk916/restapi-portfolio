from fastapi.security import (
    OAuth2AuthorizationCodeBearer,
    OAuth2PasswordRequestForm,
    OAuth2PasswordBearer,
    SecurityScopes,
)

from fastapi import APIRouter, Request, Response, Depends, HTTPException
from fastapi.responses import RedirectResponse
from uuid import uuid4

from .db import ASesDep, AsyncSession, select
from .models import User, Token, RefreshToken
from .config import JWT_EXPIRE_MIN, JWT_ALGO, SECRET_KEY, AUTH0_DOMAIN, AUTH0_API_AUDIENCE

from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from pwdlib import PasswordHash

from datetime import datetime, UTC, timedelta

import logging
import sys



logger = logging.getLogger('authlib')
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)



Hasher = PasswordHash.recommended()

tokenUrl = "/auth/token" # EXPERIMENT : Whether this is swappable or not

#refreshUrl = "/auth/refresh"
login_scheme = OAuth2PasswordBearer(
    tokenUrl=tokenUrl,
)

router = APIRouter(prefix="/auth")



def verify_password(password: str, hash: str) -> bool:
    return Hasher.verify(password, hash)

def hash_password(password: str) -> str:
    return Hasher.hash(password)

async def get_user(session: AsyncSession, username: str) -> User | None:
    user = (await session.scalars(select(User).where(User.username == username).order_by(User.id))).first()
    if user is None:
        return None
    return user

async def verify_user(session: AsyncSession, username: str, password: str) -> bool:
    user = await get_user(session, username)
    if user is None:
        return None 
    hashed = user.password
    if not verify_password(password, hashed):
        return None
    return user

async def init_token(user: User) -> Token:
    try:
        exp = datetime.now(UTC) + timedelta(minutes=JWT_EXPIRE_MIN)
        payload = {"sub": user.username, "exp": exp}
        access_token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGO)
        token = Token(access_token=access_token, token_type="bearer")
        return token
    except (ValidationError, TypeError):
        raise HTTPException(status_code=500, detail="Token failure")

async def check_token(session: ASesDep, token: Annotated[str, Depends(login_scheme)]) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGO])
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(status_code=401, detail="Missing credential")
        if exp <= datetime.now(UTC):
            raise HTTPException(status_code=401, detail="Expired")
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Missing credential")        
    except (InvalidTokenError, ValidationError):
        raise HTTPException(status_code=401, detail="Internal Error")

    user = await get_user(session, username)
    if user is None:
        raise HTTPException(status_code=401, detail="Unknown user")
    return user

@router.post("/token")
async def login(session: ASesDep, form: Annotated[OAuth2PasswordRequestForm,Depends()]):
    user = await verify_user(session, form.username, form.password)
    if user is None:
        raise HTTPException(status_code=401)
    token = await init_token(user)
    return token
    
