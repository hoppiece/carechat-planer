from logging import getLogger

from firebase_admin import firestore  # type: ignore
from linebot.v3.messaging import ReplyMessageRequest, TextMessage  # type: ignore
from linebot.v3.webhooks import FollowEvent  # type: ignore

from planer_bot.config import db, handler, line_bot_api
from planer_bot.views.richmenu import get_default_richmenu_id, link_rich_menu_to_user

logger = getLogger("uvicorn.app")


@handler.add(FollowEvent)
async def handle_follow(event: FollowEvent) -> None:
    user_profile = await line_bot_api.get_profile(event.source.user_id)
    line_identifier: str = event.source.user_id
    line_display_name: str = user_profile.display_name

    logger.info(f"FollowEvent. {line_identifier=}, {line_display_name=}")
    default_richmenu_id = await get_default_richmenu_id()
    link_rich_menu_to_user(line_identifier, default_richmenu_id)

    welcome_message_1 = f"{line_display_name}さん、友達登録ありがとうございます✨"
    welcome_message_2 = "AIケアプラン作成のデモアプリです。"
    welcome_message_3 = (
        "↓メニューをタップで開始します。リセットして最初からやり直す場合も同様です。"
    )

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
    user_ref = db.collection("users").document(line_identifier)
    user_ref.set(
        {
            "line_display_name": line_display_name,
            "line_identifier": line_identifier,
            "created_at": firestore.SERVER_TIMESTAMP,
            "count_generate_care_plan": 0,
        }
    )
    logger.info(f"User information saved. {line_identifier=}")
