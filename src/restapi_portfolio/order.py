
from .models import (
    Item,
    AddItem,
    UpdateItem,
    User,
    ItemPublic,
    Order
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

router = APIRouter(tags=["Order"])


@router.get("/orders")
async def get_orders(
        session: ASesDep,
        start: Annotated[int, Query()],
        limit: Annotated[int, Query()]) -> Sequence[Order]:
    orders = (await session.scalars(select(Order).order_by(Order.id).offset(start).limit(limit))).all()
    if not orders:
        raise HTTPException(status_code=404, detail="Not Found Any")
    return orders

@router.get("/orders/{name}")
async def get_orders_by_username(
        session: ASesDep,
        name: str) -> Sequence[Order]:

    orders = (await session.scalars(select(Order).join(User.items).where(User.username == name).order_by(Order.id))).all()
    if not orders:
        raise HTTPException(status_code=404)
    return orders

# claims: Annotated[dict, Depends(auth0.require_auth(scopes="create:orders"))],
@router.post("/order", status_code=201)
async def create_order_per_user(
    session: ASesDep,
    username: str,
    items: Annotated[list[str], Query()]
):
    if not items:
        raise HTTPException(status_code=400)
    

    user_db = await session.scalar(select(User).where(User.username == username).options(selectinload(User.items)).limit(1))
    if user_db is None:
        raise HTTPException(status_code=404)

    items_db = (await session.scalars(select(Item).where(Item.name.in_(items)))).all()
    if not items_db:
        raise HTTPException(status_code=404, detail="Not Found Any")

    for item in items_db:
        user_db.items.append(item)

    session.add(user_db)
    await session.commit()
    return {"ok": True}

#claims: Annotated[dict,Depends(auth0.require_auth(scopes="delete:orders"))],
@router.delete("/order")
async def delete_order_per_user(
    session: ASesDep,
    name: str,
    items: Annotated[list[str], Query()]
):


    user = (await session.scalar(select(User).join(User.items).where(User.username == name).options(selectinload(User.items))))
    if user is None:
        raise HTTPException(status_code=404)

    items = (await session.scalars(select(Item).where(Item.name.in_(items)))).all()
    if not items:
        raise HTTPException(status_code=404)

    for item in items:
        user.items.remove(item)

    session.add(user)
    await session.commit()
    return {"ok": True}
