from linebot.v3.webhooks import PostbackEvent, MessageEvent
from planer_bot.config import db, line_bot_api, openai_client
from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    ShowLoadingAnimationRequest,
)
from planer_bot.views.flexmessage_list import generate_list_flex_bubble

from planer_bot.gpt import answer_to_user_prompt_from_secretary


async def process_secretary(event: PostbackEvent | MessageEvent) -> None:
    line_identifier = event.source.user_id  # type: ignore

    user_ref = db.collection("users").document(line_identifier)
    user_info = user_ref.get().to_dict()
    user_state = user_info.get("state")

    if isinstance(event, MessageEvent):
        user_text = event.message.text  # type: ignore
        postback_data = None

    elif isinstance(event, PostbackEvent):
        postback_data = event.postback.data
        user_text = ""

    if postback_data == "secretary":
        # 「ケアマネ秘書」をタップした場合
        # User state の初期化と、最初の質問の提示

        user_ref.set({"state": "wait_query_to_secretary"}, merge=True)

        await line_bot_api.reply_message(
            ReplyMessageRequest( # type: ignore
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text="質問カテゴリを選択してください"),
                    FlexMessage(
                        alt_text="質問カテゴリを選択してください",
                        contents=generate_list_flex_bubble(
                            labels = [
                                "医師・看護師に質問",
                                "歯科医師に質問",
                                "薬剤師に質問",
                                "栄養士に質問",
                            ],
                            input_option="openKeyboard",
                            fill_in_text=True,
                        ),
                    ),
                ],
            )
        )

    if user_state == "wait_query_to_secretary":
        # ケアマネ秘書に質問をする場合
        # User state の初期化と、最初の質問の提示

        user_ref.set({"state": None}, merge=True)
        await line_bot_api.show_loading_animation(
            ShowLoadingAnimationRequest(chatId=line_identifier)
        )

        answer = answer_to_user_prompt_from_secretary(openai_client, user_text)
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text=answer),
                ],
            )
        )
