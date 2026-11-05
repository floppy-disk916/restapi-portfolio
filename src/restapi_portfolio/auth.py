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
from .config import JWT_EXPIRE_MIN, JWT_ALGO, PUBLIC_KEY, PRIVATE_KEY

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

async def init_access_token(data: dict, expire_min: timedelta | None = None) -> Token:
    to_encode = data.copy()
    if expire_min:
        expire = datetime.now(UTC) +  expire_min
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    access_token = jwt.encode(to_encode, PRIVATE_KEY, algorithm=JWT_ALGO)
    return access_token

async def check_token(session: ASesDep, token: Annotated[str, Depends(login_scheme)]) -> User:
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[JWT_ALGO])
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(status_code=401, detail="Missing credential")
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
    ACCESS_TOKEN_EXPIRE_MIN = timedelta(minutes=JWT_EXPIRE_MIN)
    access_token = await init_access_token({"sub": user.username}, ACCESS_TOKEN_EXPIRE_MIN)
    return Token(access_token=access_token, token_type="bearer")
    
