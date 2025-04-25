from logging import getLogger

from linebot.v3.webhooks import PostbackEvent  # type: ignore

from planer_bot.config import handler
from planer_bot.process_careplan import process_care_plan
from planer_bot.process_secretary import process_secretary

logger = getLogger("uvicorn.app")


@handler.add(PostbackEvent)
async def handle_postback(event: PostbackEvent) -> None:  # type: ignore[no-any-unimported]
    line_identifier = event.source.user_id
    logger.info(f"PostbackEvent. {line_identifier=}, {event.postback.data=}")

    postback_data = event.postback.data

    if postback_data == "create_care_plan":
        await process_care_plan(event)
    elif postback_data == "secretary":
        await process_secretary(event)
