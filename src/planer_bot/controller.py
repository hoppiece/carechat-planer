from logging import getLogger

from fastapi import APIRouter, HTTPException, Request
from linebot.v3.exceptions import InvalidSignatureError  # type: ignore

from planer_bot.config import handler

logger = getLogger("uvicorn.app")

router = APIRouter()

@router.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


@router.post("/webhook")
async def handle_callback(request: Request) -> str:
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body_raw = await request.body()
    body = body_raw.decode()

    logger.info(f"body: {body}")
    try:
        await handler.handle(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return "OK"
