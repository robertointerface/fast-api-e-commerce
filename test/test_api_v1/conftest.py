import os
import asyncio
import random
from typing import List, Dict

import pymongo
import pytest
import json
from pathlib import Path
from bson.objectid import ObjectId
from src.database_io.database_connection import MongoDbLocalConnection
from src.database_io import database_connection as mongo_init
import motor.motor_asyncio
from src.api.api_v1.endpoints.models.model_enums import OrderStatus
random.seed()


"""Empty the database for every test, Note that we have an ASYNC and a SYNC  
connection to pymongo so we can do calls to database in async and sync way."""
@pytest.fixture(autouse=True)
async def replace_mongodb_with_mockdb():
    if mongo_init.MONGO_CONNECTION is None:
        mongo_connection = MongoDbLocalConnection()
        connection_string = mongo_connection.get_connection_string()
        async_client = motor.motor_asyncio.AsyncIOMotorClient(connection_string)
        mongo_init.MONGO_CONNECTION = async_client
        mongo_init.SYNC_MONGO_CONNECTION = pymongo.MongoClient(connection_string)
    # here we don't delete/stop the connection to mongoengine, what we do
    # is delete the data inside the database but we still keep the connection
    # IS IMPORTANT THAT YOU AWAIT FOR THE drop_database OTHERWISE TESTS MIGHT
    # FAIL AS THEY ARE NOT SYNCHRONIZE AND THE DATABASE CAN BE DROPING THE
    # DATA WHILE TESTS ARE BEING DONE AND THAT RAISES UNEXPECTED ERRORS
    await mongo_init.MONGO_CONNECTION.drop_database(mongo_init.ECOMMERCE_DATABASE_NAME)


@pytest.fixture
def products_list():
    """Get dummy product list"""
    products_data = Path(__file__).parent / 'test_data' / 'test_products_data.json'
    return json.loads(products_data.read_text())


@pytest.fixture
def address():
    """Get dummy address"""
    address_data = Path(__file__).parent / 'test_data' / 'test_delivery_address.json'
    return json.loads(address_data.read_text())


@pytest.fixture()
async def set_products_data(products_list) -> List[Dict]:
    """Save dummy products data on database"""
    db = mongo_init.MONGO_CONNECTION[mongo_init.ECOMMERCE_DATABASE_NAME]
    _ = await db.products.insert_many(products_list)
    return products_list


@pytest.fixture()
async def insert_order(set_products_data, address) -> ObjectId:
    """Insert dummy order on database"""
    db = mongo_init.MONGO_CONNECTION[mongo_init.ECOMMERCE_DATABASE_NAME]
    products = [{'product_id': product['product_id'],
                 'amount':1}
                for product in set_products_data[0:2]]
    order_id = await db['orders'].insert_one(
        {"user_id": 'mario',
         "products": products,
         "delivery_address": address,
         "status": OrderStatus.ACCEPTED
         })
    return order_id.inserted_id


@pytest.fixture(scope='session')
def event_loop():
    """Fixture to modify event loop in case of async test with parametrize."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
