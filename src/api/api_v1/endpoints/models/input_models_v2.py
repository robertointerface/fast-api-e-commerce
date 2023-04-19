from pydantic import BaseModel, validator
from enum import Enum
from bson.objectid import ObjectId
from src.database_io.database_connection import (
    get_sync_database_connection,
    ECOMMERCE_DATABASE_NAME)
from src.api.api_v1.endpoints.models.model_enums import OrderStatus


class UpdateOrderStatus(BaseModel):
    order_id: str
    status: OrderStatus

    @validator("order_id")
    def check_order_exists(cls, value):
        """Validate that order exists"""
        db = get_sync_database_connection()
        ecommerce_col = db[ECOMMERCE_DATABASE_NAME]
        if not ecommerce_col.orders.count_documents({'_id': ObjectId(value)}) > 0:
            raise ValueError(f"Order  with Id: {value} does not exist")
        return value

