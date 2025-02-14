from logging import getLogger

from linebot.v3.webhooks import MessageEvent, TextMessageContent  # type: ignore

from planer_bot.config import handler

logger = getLogger("uvicorn.app")


@handler.add(MessageEvent, message=TextMessageContent)
async def message_text(event: MessageEvent) -> None:  # type: ignore[no-any-unimported]
    line_identifier = event.source.user_id
    text = event.message.text
    logger.info(f"MessageEvent. {line_identifier=}, {text=}")
