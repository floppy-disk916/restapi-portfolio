from fastapi.security import (
    APIKeyCookie,
    OAuth2AuthorizationCodeBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from fastapi import APIRouter, Request, Depends, HTTPException

from .db import ASesDep, AsyncSession, select
from .models import User
from .config import JWT_ALGO, SECRET_KEY, AUTH0_DOMAIN, AUTH0_API_AUDIENCE

from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError

from pwdlib import PasswordHash

from datetime import datetime, UTC

import logging
import sys

logger = logging.getLogger('authlib')
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

Hasher = PasswordHash.recommended()

def verify_password(password: str, hash: str) -> bool:
    return Hasher.verify(password, hash)

def hash_password(password: str) -> str:
    return Hasher.hash(password)

