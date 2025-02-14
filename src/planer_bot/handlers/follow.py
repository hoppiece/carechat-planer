from logging import getLogger

from linebot.v3.messaging import ReplyMessageRequest, TextMessage  # type: ignore
from linebot.v3.webhooks import FollowEvent  # type: ignore

from planer_bot.config import handler, line_bot_api

logger = getLogger("uvicorn.app")


@handler.add(FollowEvent)
async def handle_follow(event: FollowEvent) -> None:
    user_profile = await line_bot_api.get_profile(event.source.user_id)
    line_identifier: str = event.source.user_id
    line_display_name: str = user_profile.display_name

    logger.info(
        f"FollowEvent. {line_identifier=}, {line_display_name=}"
    )

    welcome_message_1 = f"{line_display_name}さん、友達登録ありがとうございます。"
    welcome_message_2 = "AIケアプラン作成のでもアプリです。"
    welcome_message_3 = "今から質問をいくつかしますので、お答えください。"

    await line_bot_api.reply_message(
        ReplyMessageRequest(
            replyToken=event.reply_token,
            messages=[
                TextMessage(text=welcome_message_1),
                TextMessage(text=welcome_message_2),
                TextMessage(text=welcome_message_3),
            ],
        )
    )

    # Save the user information
    # TODO
