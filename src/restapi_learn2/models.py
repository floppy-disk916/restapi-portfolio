from sqlmodel import SQLModel, UniqueConstraint, Relationship, Field
from pydantic import BaseModel
from uuid import UUID, uuid4
from datetime import UTC, datetime, timedelta

class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_id: UUID | None = Field(default=None, foreign_key="user.id", primary_key=True)
    item_id: UUID | None = Field(default=None, foreign_key="item.id", primary_key=True)
    create_at: datetime = Field(default_factory=datetime.now(UTC))
 
class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(SQLModel):
    id: UUID
    username: str
    password: str


class User(UserBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    items: list[Item] = Relationship(back_populates="customers", link_model=Order)
    
    __table_args__ = (
        UniqueConstraint("username",name="uq_username"),
        )



class AddUser(BaseModel):
    username: str
    password: str

class UpdateUser(BaseModel):
    username: str | None = None
    password: str | None = None

class UserPublic(BaseModel):
    id: UUID
    username: str

class ItemBase(SQLModel):
    id: UUID
    name: str
    price: float
    tax: float
    
class Item(ItemBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    customers: list[User] = Relationship(back_populates="items", link_model=Order)
  
class UpdateItem(BaseModel):
    name: str | None = None
    price: float | None = None
    tax: float | None = None

class AddItem(BaseModel):
    name: str
    price: float
    tax: float

class ItemPublic(ItemBase):
    pass

