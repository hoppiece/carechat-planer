import urllib.parse
from logging import getLogger

from linebot.v3.webhooks import PostbackEvent  # type: ignore

from planer_bot import models
from planer_bot.config import handler, line_bot_api

# from hygeia_ai.service_plan_2 import generate_plan

logger = getLogger("uvicorn.app")


def get_form_url_add_new_patient(line_identifier: str) -> str:
    form_url_base = "https://docs.google.com/forms/d/e/1FAIpQLSedKqPBPeqQnP-ty43t--x1DBXcKyKcsBs7B_olOlG10VGTaw/viewform?usp=pp_url&entry.892889867="
    return form_url_base + urllib.parse.quote(line_identifier)


@handler.add(PostbackEvent)
async def handle_postback(event: PostbackEvent) -> None:  # type: ignore[no-any-unimported]
    line_identifier = event.source.user_id
    action_id = models.PostBackActionData.model_validate_json(event.postback.data).action_id


    logger.info(f"PostbackEvent. {line_identifier=}, {event.postback.data=}")


    ##############
    # 状態取得
    ...


    ##############
    # リッチメニューの「最初から」をタップした場合の処理
    if action_id == models.BotAction.richmenu_最初から.value:
        ...
