from logging import getLogger

from firebase_admin import firestore  # type: ignore
from linebot.v3.messaging import (  # type: ignore
    FlexMessage,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent  # type: ignore

from planer_bot.config import db, handler, line_bot_api
from planer_bot.views.flexmessage_list import generate_list_flex_bubble

logger = getLogger("uvicorn.app")


@handler.add(MessageEvent, message=TextMessageContent)
async def message_text(event: MessageEvent) -> None:  # type: ignore[no-any-unimported]
    line_identifier = event.source.user_id
    text = event.message.text
    logger.info(f"MessageEvent. {line_identifier=}, {text=}")

    user_ref = db.collection("users").document(line_identifier)
    user_info = user_ref.get().to_dict()
    if text == "スタート":
        user_ref.update({"count_generate_care_plan": firestore.Increment(1), "answers": {
                "question_1": None,
                "question_2": None,
                "question_3": None,
                "question_4": None,
                "question_5": None,
                "question_6": None,
                "question_7": None,
                "question_8": None,
            },
            "state": "wait_q1"})

        await line_bot_api.reply_message(
            ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(text="それでは、いくつか質問をするので回答をお願いします。質問は合計で8つです。"),
                TextMessage(text="Q.1 現在、生活の中で特に困っていることや、解決したい課題を教えてください。")
            ],
            )
        )


    if user_info.get("state") == "wait_q1":
        user_ref.update({"answers.question_1": text, "state": "wait_q2"})
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text="Q.2 介護に関して、ご家族としての希望や意向を教えてください。"),
                ],
            )
        )

    elif user_info.get("state") == "wait_q2":
        user_ref.update({"answers.question_2": text, "state": "wait_q3"})
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text="Q.3 現在の要介護度を選択してください。"),
                    FlexMessage(
                        altText="Q.3 現在の要介護度を選択してください。",
                        contents=generate_list_flex_bubble(labels=[
                            "要介護1",
                            "要介護2",
                            "要介護3",
                            "要介護4",
                            "要介護5",
                            "申請中 / 不明",
                        ]),
                    )
                ],
            )
        )

    elif user_info.get("state") == "wait_q4_other":
        user_ref.update({"answers.question_4": text, "state": "wait_q5"})
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text="Q.5 現在、利用している介護サービスがあれば選択してください。"),
                    FlexMessage(
                        altText="Q.5 現在、利用している介護サービスがあれば選択してください。",
                        contents=generate_list_flex_bubble(labels=[
                            "何も利用していない",
                            "訪問介護",
                            "デイサービス",
                            "ショートステイ",
                            "訪問リハビリ",
                            "訪問看護",
                            "施設入所（特養・老健・有料老人ホームなど）",
                            "その他 (自由入力)",
                        ], text_align="flex-start"),
                    )
                ],
            )
        )
    elif user_info.get("state") == "wait_q5_other":
            user_ref.update({"answers.question_5": text, "state": "wait_q6"})
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text="Q.6 ご自宅の環境について、移動しにくい場所や危険な箇所はありますか？"),
                        FlexMessage(
                            altText="ご自宅の環境について、移動しにくい場所や危険な箇所はありますか？",
                            contents=generate_list_flex_bubble(labels=[
                                "特に問題なし",
                                "トイレまでの移動が大変",
                                "段差が多く、転倒しやすい",
                                "手すりが必要",
                                "ベッドから起き上がりがつらい",
                                "ポータブルトイレを検討したい",
                                "その他 (自由入力)",
                            ], text_align="flex-start"),
                        )
                    ],
                )
            )
    elif user_info.get("state") == "wait_q6_other":
            user_ref.update({"answers.question_6": text, "state": "wait_q7"})
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text="Q.7 現在、介護をしているのはどなたですか？また、介護負担の状況を教えてください。"),
                        FlexMessage(
                            altText="Q.7 現在、介護をしているのはどなたですか？また、介護負担の状況を教えてください。",
                            contents=generate_list_flex_bubble(labels=[
                                "本人が一人で生活している（独居）",
                                "家族（同居）が主に介護している",
                                "家族（別居）が定期的に介護している",
                                "介護負担が大きくなってきた（サポートが必要）",
                                "夜間の介護が負担になっている",
                                "その他 (自由入力)",
                            ], text_align="flex-start"),
                        )
                    ],
                )
            )
    elif user_info.get("state") == "wait_q7_other":
            user_ref.update({"answers.question_7": text, "state": "wait_q8"})
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text="Q.8 介護保険の自己負担割合（1割～3割）や、負担限度額認定の申請状況を教えてください。"),
                        FlexMessage(
                            altText="Q.8 介護保険の自己負担割合（1割～3割）や、負担限度額認定の申請状況を教えてください。",
                            contents=generate_list_flex_bubble(labels=[
                                "1割負担",
                                "2割負担",
                                "3割負担",
                                "生活保護を受給している（自己負担なしの場合あり）",
                                "負担限度額認定の申請済み",
                                "負担限度額認定の申請はしていない / 不明"
                            ], text_align="flex-start"),
                        )
                    ],
                )
            )
