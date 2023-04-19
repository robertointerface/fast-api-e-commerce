import pytest
import json
from src.main import app
from typing import Optional, List, Union
from httpx import AsyncClient
from src.database_io.database_connection import (
    get_database_connection,
    ECOMMERCE_DATABASE_NAME)
from bson.objectid import ObjectId
from src.api.api_v1.endpoints.models.model_enums import OrderStatus


class TestOrdersEndpoints:
    """Test Orders API end points"""

    async def get_order_by_id(self, order_id: Union[ObjectId, str]):
        """Get an order from database by providing the ID"""
        if isinstance(order_id, str):
            order_id = ObjectId(order_id)
        database_client = get_database_connection()
        db = database_client[ECOMMERCE_DATABASE_NAME]
        return await db.orders.find_one({"_id": order_id})

    @pytest.mark.unit
    async def test_get_order_status(self, insert_order: ObjectId):
        """Test endpoint get-order-status returns expected status"""
        requested_order_info = await self.get_order_by_id(insert_order)
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f'/api/v1/orders/get-order-status/{str(insert_order)}')
            response_content = json.loads(response.content)
            assert response_content['orderStatus'] == requested_order_info['status']

    @pytest.mark.unit
    async def test_get_order_status_returns_error_if_not_found(self, insert_order: ObjectId):
        """Test endpoint get-order-status returns message 'Order not found' when
        the provided order id is not valid.
        """
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f'/api/v1/orders/get-order-status/{str(insert_order)[::-1]}')
            assert response.status_code == 404
            response_content = json.loads(response.content)
            assert response_content['detail'] == "Order not found"

    @pytest.mark.unit
    async def test_update_order_status(self, insert_order: ObjectId):
        """test endpoint update-order-status updates status, first call
        api then reload the order data from database to validate it has been
        updated correctly."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            update_input = {
                "order_id": str(insert_order),
                "status": OrderStatus.DISPATCHED
            }
            response = await ac.put(
                f'/api/v1/orders/update-order-status',
                json=update_input)
            assert response.status_code == 200
        updated_order = await self.get_order_by_id(insert_order)
        assert updated_order["status"] == OrderStatus.DISPATCHED

    @pytest.mark.skip
    @pytest.mark.unit
    async def test_create_order_saves_order_when_correct_input(self,
                                                               set_products_data,
                                                               address):
        products_ids = [product['product_id']
                        for product in set_products_data[0:3]]
        order_input = {
            "user_id": 'Mario',
            "products": [{"product_id": p_id, "amount": 1}
                         for p_id in products_ids],
            "delivery_address": address
        }
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(f'/api/v1/orders/create-order',
                                     json=order_input)
            assert response.status_code == 201
            response_content = json.loads(response.content)
            created_order = await self.get_order_by_id(response_content["order_id"])
            assert created_order is not None
