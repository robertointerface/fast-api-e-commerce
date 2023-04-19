from fastapi import FastAPI
from mangum import Mangum
from src.api.api_v1.api import router as api_router

app = FastAPI()

app.include_router(api_router, prefix="/api/v1")

# aws lambda handler
#handler = Mangum(app)