from fastapi import FastAPI
from routes import base,data
from helpers.config import get_settings

settings = get_settings()


app = FastAPI()
app.include_router(base.base_router)
app.include_router(data.data_router)