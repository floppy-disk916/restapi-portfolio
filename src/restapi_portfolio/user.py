
from .models import (
    User,
    AddUser,
    UpdateUser,
    Item,
    UserPublic
)

from .auth import hash_password
from .db import ASesDep, select, insert, update, delete
from sqlalchemy.orm import selectinload

from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException,
)

from .cache import (
    get_from_cache,
    set_to_cache,
    inval_cache
)

from typing import Annotated
from collections.abc import Sequence

router = APIRouter(tags=["User"])

@router.post("/user", status_code=201)
async def create_user(
    session: ASesDep,
    users: Sequence[AddUser]
):
    if not users:
        raise HTTPException(status_code=400)
    
    users_db = []
    for user in users:
        user.password = hash_password(user.password)
        users_db.append(User.model_validate(user))

    session.add_all(users_db)
    return {"ok": True}



@router.get("/users")
async def get_users(
        session: ASesDep,
        start: Annotated[int, Query()],
        limit: Annotated[int, Query()]) -> Sequence[UserPublic]:
    users = (await session.scalars(select(User).order_by(User.id).offset(start).limit(limit).options(selectinload(User.items)))).all()
    if not users:
        raise HTTPException(status_code=404, detail="Not Found Any")
    return users

# claims: Annotated[dict, Depends(auth0.require_auth(scopes="create:users"))],
@router.get("/user/{name}")
async def get_user_by_name(
        session: ASesDep,
        name: str
    ) -> UserPublic:
    
    tag = f"user:{name}"
    user = await get_from_cache(tag)
    if user is not None:
        return UserPublic.model_validate_json(user)

    user = (await session.scalar(select(User).where(User.username == name).limit(1)))
    if user is None:
        raise HTTPException(status_code=404)

    await set_to_cache(tag, user.model_dump_json())
    return user

@router.get("/users/{prod_name}")
async def get_users_by_product_name(
        session: ASesDep,
        prod_name: str,
    ) -> Sequence[UserPublic]:
    users = (await session.scalars(select(User).join(User.items).where(Item.name == prod_name))).all()
    if not users:
        raise HTTPException(status_code=404)
    return users

@router.put("/user/{name}")
async def update_user(
    session: ASesDep,
    name: str,
    user: UpdateUser
) -> UserPublic:
    user_db = await session.scalar(select(User).where(User.username == name))
    if not user_db:
        raise HTTPException(status_code=404)

    new = user.model_dump()
    for key, value in new.items():
        if value is None:
            raise HTTPException(status_code=400, detail="Partial data")

        if key == "password":
            value = hash_password(value)
        setattr(user_db, key, value)

    session.add(user_db)
    tag = f"user:{name}"
    await set_to_cache(tag, user_db.model_dump_json())


    return user_db


@router.patch("/user/{name}")
async def partial_update_user(
    session: ASesDep,
    name: str,
    user: UpdateUser
) -> UserPublic:
    
    user_db = await session.scalar(select(User).where(User.username == name))
    if not user_db:
        raise HTTPException(status_code=404)
    new = user.model_dump(exclude_unset=True)
    
    for key, value in new.items():
        if key == "password":
            value = await hash_password(value)
        setattr(user_db, key, value)

    session.add(user_db)
 
    tag = f"user:{name}"
    await set_to_cache(tag, user_db.model_dump_json())
    return user_db

# claims: Annotated[dict,Depends(auth0.require_auth(scopes="delete:users"))],
@router.delete("/user")
async def delete_user(
    session: ASesDep,
    names: Annotated[list[str], Query()],
):
    users = (await session.scalars(select(User).where(User.username.in_(names)))).all()
    if not users:
        raise HTTPException(status_code=404)
    await session.delete_all(users)
    
    for user in users:
        tag = f"user:{user.username}"
        await inval_cache(tag)

    return {"ok": True}
