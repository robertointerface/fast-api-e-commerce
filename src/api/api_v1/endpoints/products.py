"""Product endpoints"""
from typing import Annotated, Union

from fastapi import (
    APIRouter,
    Query,
    Path,
    HTTPException,
    status, Depends)
from fastapi.responses import JSONResponse

from src.api.api_v1.endpoints.models.output_models import AvailableProduct
from src.database_io.database_connection import (
    get_database_connection,
    ECOMMERCE_DATABASE_NAME)
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


def fake_decode_token(token):
    return User(
        username=token + "fakedecoded",
        email="john@example.com",
        full_name="John Doe"
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    return user


@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


"""As you can see below we have the endpoints available_product & 
discount_product_count that use the inputs a different way to do it is by using
the dependencies on fast api and define these common parameter"""
async def common_parameters(product_id: str = Path(min_length=5,
                                                   title='product id'),
                            count: int = Query(ge=1, default=1)):
    return {'product_id': product_id, 'count': count}


@router.get("/available-product/{product_id}", status_code=status.HTTP_200_OK)
async def available_product(product_id: str = Path(min_length=5,
                                                   title='product id'),
                            count: int = Query(ge=1)) -> AvailableProduct:
    """Ask if there are enough items of specific product on inventory.

    Connect to database, get the product and verify if we have enough items
        of that product on inventory.
    Args:
        product_id: Product id
        count: amount that we want to know if there are enough on inventory.
    """
    database_client = get_database_connection()
    db = database_client[ECOMMERCE_DATABASE_NAME]
    product = await db.products.find_one(
        {'product_id': product_id}
    )
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product with product id = {product_id} "
                                   f"does not exist")
    product_is_available = product['available_count'] >= count
    return AvailableProduct(is_available=product_is_available)


@router.put("/discount-product-count/{product_id}",
            status_code=status.HTTP_200_OK)
async def discount_product_count(product_id: str = Path(min_length=5,
                                                        title='product id'),
                                 count: int = 1):
    """Reduce a product storage count by the specified amount.

    If we have 5 Monitors available on the database and a user buys 2, then
        we need to reduce the available amount by 2, this API does that.

    Args:
        product_id: (String) related product id
        count: (Integer) amount to reduce the product available count.
    """
    database_client = get_database_connection()
    db = database_client[ECOMMERCE_DATABASE_NAME]
    product = await db.products.find_one(
        {'product_id': product_id}
    )
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product with product id = {product_id} "
                                   f"does not exist")
    new_available_count = product['available_count'] - count
    if new_available_count < 0:
        msg = f"discount count is bigger than available products, available " \
              f"products = { product['available_count']}"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=msg)
    await db.products.update_one(
        {'product_id': product_id},
        {'$set':
             {'available_count': new_available_count}
        }
    )
    return JSONResponse(content={"message": "Updated correctly"})