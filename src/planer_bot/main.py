from fastapi import APIRouter, FastAPI

from planer_bot import controller

api_router = APIRouter()
api_router.include_router(controller.router)

app = FastAPI()
app.include_router(api_router)

