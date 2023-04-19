"""
Define rest api input pydantic models
"""
from typing import (
    List,
    Optional)

from pydantic import BaseModel, validator

from src.api.api_v1.endpoints.models.model_enums import (
    AllowedCountries)
from src.database_io.database_connection import (
    get_database_connection,
    get_sync_database_connection,
    ECOMMERCE_DATABASE_NAME)


class Address(BaseModel):
    street_name: str
    city: str
    country: AllowedCountries
    post_code: str
    apartment: Optional[int]


class Product(BaseModel):
    product_id: str
    name: str
    price: float
    available_count: int
    type: Optional[str]
    description: Optional[str]

    @validator("product_id")
    def check_product_exists(cls, value) -> bool:
        """Check if a product exists on inventory.

        Connects database and tries to find it in inventory. we use the pymongo
            function find and limit to 1.

        Args:
            value: this is the product id

        Returns:
            True if product exists
            False if it NOT exists
        """
        db = get_database_connection()
        ecommerce_col = db[ECOMMERCE_DATABASE_NAME]
        exists = ecommerce_col.find({'product_id': value}).limit(1)
        return exists is not None


class ProductOrder(BaseModel):
    product_id: str
    amount: int


class Order(BaseModel):
    user_id: str
    products: List[ProductOrder]
    delivery_address: Address

    @validator("products", each_item=True)
    def check_products_exists(cls, product):
        """Check if a product exists on inventory.

        Connects database and tries to find it in inventory. we use the pymongo
            function count_documents which is better way than the one above.

        Args:
            value: this is the product id

        Returns:
            True if product exists
            False if it NOT exists
        """
        client = get_sync_database_connection()
        db = client[ECOMMERCE_DATABASE_NAME]
        exists = db.products.count_documents({'product_id': product.product_id}) > 0
        if not exists:
            raise ValueError(f"Product with id = {product.product_id} does not exist")


class User(BaseModel):
    user_id: str
    username: str
    address: Address
    orders: List[Order]


class OrderProduct(BaseModel):
    product_id: str
    quantity: int
    price: float
    discount: Optional[float]

    def total(self):
        pass
