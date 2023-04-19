"""
API Order operations
"""
from bson.objectid import ObjectId
from fastapi import (
    APIRouter,
    Path,
    status)
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from src.api.api_v1.endpoints.models.input_models import (
    Order)
from src.api.api_v1.endpoints.models.input_models_v2 import UpdateOrderStatus
from src.api.api_v1.endpoints.models.output_models import SavedOrderId
from src.database_io.database_connection import (
    get_database_connection,
    get_sync_database_connection,
    ECOMMERCE_DATABASE_NAME)

router = APIRouter()


@router.post('/create-order', status_code=status.HTTP_201_CREATED)
async def create_order(order: Order) -> SavedOrderId:
    """Create an order.

    Validate order input data and save on mongoDB database

    Args:
        order: Pydantic Basemodel Order, we use pydantic validator functionality
            to validate that all products on the order exist.
    """
    database_client = get_database_connection()
    db = database_client[ECOMMERCE_DATABASE_NAME]
    created_order_id = await db.orders.insert_one(order.dict())
    return SavedOrderId(order_id=str(created_order_id.inserted_id))


# here you could do the same with url /update-order-status/{order_id}?status={status}
# but Just want to show you can do it this way also
@router.put('/update-order-status',
            status_code=status.HTTP_200_OK)
async def update_order_status(update_status: UpdateOrderStatus):
    """Update an order status.

    Args:
        update_status: Pydantic BaseModel with the order id and the new status.
            class checks the field order id to validate that it exists
    """
    database_client = get_sync_database_connection()
    db = database_client[ECOMMERCE_DATABASE_NAME]
    _ = db.orders.update_one({"_id": ObjectId(update_status.order_id)},
                             {"$set": {"status": update_status.status}})


"""Another option here is to return None and let the user handle it."""
@router.get('/get-order-status/{order_id}', status_code=status.HTTP_200_OK)
async def get_order_status(order_id: str = Path(max_length=24,
                                                min_length=24,
                                                title='order id')):
    """Get teh order status by providing the order id.

    Args:
        order_id: order id

    Returns: Json response with content {"orderStatus": order['status']}

    Raises:
        HTTPException: If order not found.
    """
    database_client = get_database_connection()
    db = database_client[ECOMMERCE_DATABASE_NAME]
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return JSONResponse(content={"orderStatus": order['status']},
                        status_code=status.HTTP_200_OK)
