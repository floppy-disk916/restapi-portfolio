

from fastapi import APIRouter
from .user import router as user_router
from .item import router as item_router
from .order import router as order_router

router = APIRouter(prefix="/api")

router.include_router(user_router)
router.include_router(item_router)
router.include_router(order_router)
