from datetime import datetime
from typing import Annotated, Union, List
from fastapi import (
    APIRouter,
    Query,
    Path)
from src.api.api_v1.endpoints.models.input_models import Order
from fastapi import APIRouter

router = APIRouter()


@router.get("/user-orders")
async def get_users_orders(
        start_date: Annotated[Union[datetime, None],
                              Query(description='start date')] = None,
        end_date: Annotated[Union[datetime, None],
                            Query(description='end date')] = None) -> List[Order]:
    pass


@router.get("/user-info")
async def get_user():
    pass