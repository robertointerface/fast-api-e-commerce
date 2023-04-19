from fastapi import APIRouter
from src.api.api_v1.endpoints import users
from src.api.api_v1.endpoints import products
from src.api.api_v1.endpoints import orders
router = APIRouter()

router.include_router(users.router,
                      prefix="/users",
                      tags=["Users"])

router.include_router(products.router,
                      prefix="/products",
                      tags=["Products"])

router.include_router(orders.router,
                      prefix="/orders",
                      tags=["Orders"])
