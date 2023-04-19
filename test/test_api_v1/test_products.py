import json
import random
import pytest
from src.main import app
from httpx import AsyncClient
from src.database_io.database_connection import (
    get_database_connection,
    ECOMMERCE_DATABASE_NAME)


async def find_product_by_id(product_id):
    database_client = get_database_connection()
    db = database_client[ECOMMERCE_DATABASE_NAME]
    return await db.products.find_one(
        {'product_id': product_id}
    )


@pytest.mark.unit
@pytest.mark.parametrize('extra_count,expected_availability',
                         [
                             (0, True),
                             (1000, False)
                         ]
                         )
async def test_endpoint_available_product_returns_correct_response(
        set_products_data,
        extra_count,
        expected_availability,
        event_loop):
    """Test endpoint available-product returns True when expected."""
    saved_product = set_products_data[random.randint(0, 2)]
    product_id = saved_product['product_id']
    product_available_count = saved_product['available_count']
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f'/api/v1/products/available-product/{product_id}?count={product_available_count + extra_count}')
    assert response.status_code == 200
    response_content = json.loads(response.content)
    assert response_content['is_available'] is expected_availability, \
        f"Product with id {product_id} should be available = {expected_availability} " \
        f"available count = {product_available_count}, requested count = {product_available_count + extra_count}"


@pytest.mark.unit
async def test_endpoint_available_products_returns_404_when_invalid_product_id(set_products_data):
    """Test endpoint available-product raises error when expected"""
    invalid_product_id = "Picachu"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            f'/api/v1/products/available-product/{invalid_product_id}?count={2}')
    assert response.status_code == 404, \
        f"product with id = {invalid_product_id} does not exist, response should" \
        f" be 404"


@pytest.mark.unit
async def test_endpoint_discount_product_count(set_products_data):
    """Test endpoint discount-product-count updates product correctly."""
    saved_product = set_products_data[random.randint(0, 2)]
    product_id = saved_product['product_id']
    product_available_count = saved_product['available_count']
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(f'/api/v1/products/discount-product-count/{product_id}?count={1}')
    assert response.status_code == 200
    updated_product = await find_product_by_id(product_id)
    assert updated_product['available_count'] == product_available_count - 1