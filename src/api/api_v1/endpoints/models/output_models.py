from typing import Union, Annotated, Any, List,  Optional
from pydantic import BaseModel
from src.api.api_v1.endpoints.models.input_models import Address
from src.api.api_v1.endpoints.models.model_enums import OrderStatus


class AvailableProduct(BaseModel):
    is_available: bool


class SavedOrderId(BaseModel):
    order_id: str


class Product(BaseModel):
    product_id: str
    name: str
    price: float
    available_count: int
    type: Optional[str]
    description: Optional[str]


class Order(BaseModel):
    user_id: str
    products: List[Product]
    delivery_address: Address
    status: OrderStatus


class UserOrders(BaseModel):
    username: str
    orders: List[Order]
