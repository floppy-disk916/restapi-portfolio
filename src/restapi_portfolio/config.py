from dotenv import load_dotenv
import os


load_dotenv()


err = "Invalid variable. Please check if the variable exists or is valid"

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(err)

REDIS_URL = os.environ.get("REDIS_URL")
if not REDIS_URL:
    raise RuntimeError(err)

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(err)

PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
if not PRIVATE_KEY:
    raise RuntimeError(err)

PUBLIC_KEY = os.environ.get("PUBLIC_KEY")
if not PUBLIC_KEY:
    raise RuntimeError(err)

JWT_ALGO = os.environ.get("JWT_ALGO")
if not JWT_ALGO:
    raise RuntimeError(err)

JWT_EXPIRE_MIN = os.environ.get("JWT_EXPIRE_MIN")
if not JWT_EXPIRE_MIN:
    raise RuntimeError(err)
else:
    JWT_EXPIRE_MIN = int(JWT_EXPIRE_MIN)
