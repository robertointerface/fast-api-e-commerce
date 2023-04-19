from enum import Enum
from typing import Union, Annotated, Any
from fastapi import FastAPI, Body, Depends
from fastapi import Query, Path
from pydantic import BaseModel
from typing import Optional
from src.api.api_v1.api import router as api_router
from mangum import Mangum
from fastapi.security  import OAuth2PasswordBearer

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/items-secret")
async def read_items(token: str = Path(Depends(oauth2_scheme))):
    return {"token": token}

@app.get("/")
async def root():
    return {"message": "Hello World"}



class Item(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    tax: Optional[float] = None

"""
REQUEST BODY, you can define the post/put/patch  request bodies with pydantic dataclass
as above with Item, this way you let pydantic take care of data validation.

"""

@app.post("/items")
async def create_item(item: Item):
    item.price = 40000
    return item

"""you can define the path parameter and the request body and fastapi recognizes which is which"""
@app.post("/items/{item_id}")
async def create_item_with_id(item_id: str, item: Item):
    item_dict = item.dict()
    return {'item_id': item_id, 'item_data': item_dict}

"""You can use path parameters, request body and query parameters all at once like below
"""
@app.put("/items/{item_id}")
async def create_item_with_id(item_id: str, item: Item, q: str):
    item_dict = item.dict()
    return {'item_id': item_id, 'item_data': item_dict}


#QUERY PARAMETERS
# when you define parameters after path parameters, these are treated as query params
# below is http://127.0.0.1:8000/hello/roberto?q=testing&s=doom
@app.get("/hello/{name}")
async def say_hello(name: str, q: Union[str, None], s: Union[str, None]):
    return {"message": f"Hello {name}", "q": q, "s": s}

# parameters can be optional, in the case below, q is compulsary but 's' is optional
# @app.get("/hello/{name}")
# async def say_hello(name: str, q: Union[str, None], s: Union[str, None] = None):
#     if s:
#         return {"message": f"Hello {name}", "q": q, "s": s}
#     return {"message": f"Hello {name}", "q": q}

# you can add further validation to a query parameter


# use as below to add extra validation, for more examples look at documentation
# https://fastapi.tiangolo.com/tutorial/query-params-str-validations/#__tabbed_18_2
@app.get("/hello2/{name}")
async def say_hello(name: str = Path(max_length=3, title="name of person"),
                    q: Union[str, None] = Query(max_length=5, default=None),
                    s: Union[str, None] = None):
    if s:
        return {"message": f"Hello {name}", "q": q, "s": s}
    return {"message": f"Hello {name}", "q": q}

# you can do numbers validation
@app.get("/pay_price/{amount}")
async def pay_price_func(amount: int = Path(gt=0)):
    return {"amount": amount}


@app.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"item_id": item_id}


# you can make paths compulsary values with the below way.
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.lenet:
        return {"message": "dragon ball"}
    if model_name == ModelName.resnet:
        return {"message": "futurama"}

############RESPONSE #######################3
"""
You can set the response type as below, then the return will be validated
"""

@app.get("/models/{fist_model}")
async def get_first_model(first_model: str) -> Item:
    item = Item(
        name='item',
        price=22.4,
        description='dee',
        tax=34.43
    )
    return item

"""use response model when you want fastApi to do filtering for you on the output response"""


class ItemNoTax(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

"""In the example below we return object of type Item wich has attribute 'tax' BUT as we define the output type 
of type ItemNoTax that has no attribute tax, fastapi when using response_model  will filter this automatically and
remove the attribute 'tax' on the response"""
@app.post("/saveModels/{fist_model}", response_model=ItemNoTax)
async def get_first_model(item: Item) -> Any:
    return item

# you can also return redirects or Json response directly
from fastapi.responses import JSONResponse, RedirectResponse

@app.get("/get_model/{first_model}")
async def get_model(first_model: str):
    return JSONResponse(content={"message": "you requested a model"})

# to set the return status code use as below
from fastapi import status
@app.get("/get_model/{first_model}", status_code=status.HTTP_200_OK)
async def get_model(first_model: str):
    return JSONResponse(content={"message": "you requested a model"})



app.include_router(api_router, prefix="/api/v1")
handler = Mangum(app)


