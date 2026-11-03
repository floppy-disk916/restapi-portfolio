# RestAPI Portfolio
---

A Portfolio showcasing simple CRUD based operation using:
- FastAPI for backend
- Asynchronous SQLAlchemy
- Alembic migration
- Pytest for unit testing
- Redis for caching
- Pydantic for validation

## How to run
Make sure you already have uv installed
```
git clone https://github.com/floppy-disk916/restapi-portfolio.git
cd restapi-portfolio
```
Be sure to change the .env.example according to your system
```
mv .env.example .env
uv sync
uv run alembic upgrade head
uv run fastapi run
```

## NOTE : The Portfolio is still under development
---

TODO.md file explains what it lacks of
