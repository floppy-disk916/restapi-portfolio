
from .models import (
    Item,
    AddItem,
    UpdateItem,
    User,
    ItemPublic
)

from .db import ASesDep, select, insert, update, delete
from sqlalchemy.orm import selectinload

from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException,
)

from typing import Annotated
from collections.abc import Sequence

router = APIRouter(tags=["Item"])


@router.get("/items")
async def get_items(
        session: ASesDep,
        start: Annotated[int, Query()],
        limit: Annotated[int, Query()]) -> Sequence[ItemPublic]:
    items = (await session.scalars(select(Item).order_by(Item.id).offset(start).limit(limit).options(selectinload(Item.customers)))).all()
    if not items:
        raise HTTPException(status_code=404, detail="Not Found Any")
    return items

@router.get("/item/{name}")
async def get_item_by_name(
        session: ASesDep,
        name: str) -> ItemPublic:
    item = (await session.scalar(select(Item).where(Item.name == name).limit(1)))
    if item is None:
        raise HTTPException(status_code=404)
    return item

# claims: Annotated[dict, Depends(auth0.require_auth(scopes="create:items"))],
@router.post("/item", status_code=201)
async def create_item(
    session: ASesDep,
    items: Sequence[AddItem]
):
    if not items:
        raise HTTPException(status_code=400)
    
    items_db = []
    for item in items:
        items_db.append(Item.model_validate(item))

    session.add_all(items_db)
    await session.commit()
    return {"ok": True}

@router.put("/item/{name}")
async def update_item(
    session: ASesDep,
    name: str,
    item: UpdateItem
) -> ItemPublic:
    item_db = await session.scalar(select(Item).where(Item.name == name))
    if not item_db:
        raise HTTPException(status_code=404)
    
    new = item.model_dump()
    for key, value in new.items():
        if value is None:
            raise HTTPException(status_code=400, detail="Partial data")

        setattr(item_db, key, value)
    
    session.add(item_db)
    await session.commit()
    await session.refresh(item_db)
    return item_db


@router.patch("/item/{name}")
async def partial_update_item(
    session: ASesDep,
    name: str,
    item: UpdateItem
) -> ItemPublic:
    item_db = await session.scalar(select(Item).where(Item.name == name))
    if not item_db:
        raise HTTPException(status_code=404)
    new = item.model_dump(exclude_unset=True)
    
    for key, value in new.items():
        if key == "password":
            value = await hash_password(value)
        setattr(item_db, key, value)

    session.add(item_db)
    await session.commit()
    await session.refresh(item_db)
    return item_db

# claims: Annotated[dict,Depends(auth0.require_auth(scopes="delete:items"))],
@router.delete("/item")
async def delete_item(
    session: ASesDep,
    names: Annotated[list[str], Query()],
):
    items = (await session.scalars(select(Item).where(Item.name.in_(names)))).all()
    if not items:
        raise HTTPException(status_code=404)
    await session.delete_all(items)
    await session.commit()
    return {"ok": True}
