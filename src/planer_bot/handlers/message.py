from logging import getLogger

from linebot.v3.webhooks import MessageEvent  # type: ignore
from linebot.v3.webhooks import TextMessageContent

from planer_bot.config import handler
from planer_bot.process_careplan import process_care_plan
from planer_bot.process_secretary import process_secretary

logger = getLogger("uvicorn.app")


@handler.add(MessageEvent, message=TextMessageContent)
async def message_text(event: MessageEvent) -> None:  # type: ignore[no-any-unimported]
    line_identifier = event.source.user_id
    text = event.message.text
    logger.info(f"MessageEvent. {line_identifier=}, {text=}")

    await process_care_plan(event)
    await process_secretary(event)
