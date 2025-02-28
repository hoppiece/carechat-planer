from logging import getLogger

from fastapi import APIRouter, FastAPI

from planer_bot import controller

logger = getLogger("uvicorn.app")
api_router = APIRouter()
api_router.include_router(controller.router)

app = FastAPI()
app.include_router(api_router)


logger.debug("app started")
