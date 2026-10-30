from fastapi.testclient import TestClient
from src.restapi_learn2.main import app
from src.restapi_learn2.db import engine
from httpx import AsyncClient, ASGITransport
import pytest

@app.on_event("shutdown")
async def on_shutdown():
    await engine.dispose()

client = TestClient(app)


## Item ----- 6
def test_get_items():
    params = {
        "start": 0,
        "limit": 10
    }
    response = client.get(
        "/api/items",
        params=params,
    )
    assert response.status_code >= 200 and response.status_code < 300
    assert response.json()


transport = ASGITransport(app=app, lifespan="on")

@pytest.mark.anyio
async def test_create_item():
    json1 = [{"name": "test_1","price": 1000, "tax": 20}]

    async with AsyncClient(transport=transport, base_url="http://localhost:8000") as ac:
        response = await ac.post("/api/item", json=json1)
    
    assert response.status_code >= 200 and response.status_code < 300
    
    
    async with AsyncClient(transport=transport, base_url="http://localhost:8000") as ac:
        response = client.post("/api/item", json=json1)

    assert response.status_code >= 400 and response.status_code < 500
    assert response.json()

## User ----- 7
## Order ----- 4
