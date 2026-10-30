from dotenv import load_dotenv
import os


load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
REDIS_URL = os.environ.get("REDIS_URL")
SECRET_KEY = os.environ.get("SECRET_KEY")
JWT_ALGO = os.environ.get("JWT_ALGO")
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
AUTH0_API_AUDIENCE = os.environ.get("AUTH0_API_AUDIENCE")
