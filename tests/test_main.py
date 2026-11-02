from httpx import AsyncClient
from src.restapi_learn2.db import AsyncSession
from .conftest import aiomark


async def test_create_item(
    get_client: AsyncClient,
):
    payload = [
        {   
            "name": "abc",
            "price": 0,
            "tax": 0,
        }
    ]

    response = await get_client.post("/api/item", json=payload)
    assert response.status_code >= 200 and response.status_code < 300
    assert response.json()

## Item ----- 6

## User ----- 7
## Order ----- 4
