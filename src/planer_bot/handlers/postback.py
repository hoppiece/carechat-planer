import urllib.parse
from logging import getLogger

from firebase_admin import firestore  # type: ignore
from linebot.v3.messaging import FlexMessage  # type: ignore
from linebot.v3.messaging import (PushMessageRequest, ReplyMessageRequest,
                                  ShowLoadingAnimationRequest, TextMessage)
from linebot.v3.webhooks import PostbackEvent  # type: ignore

from planer_bot.config import db, handler, line_bot_api, openai_client
from planer_bot.gpt import anwer_to_care_planer
from planer_bot.views.flexmessage_list import generate_list_flex_bubble

# from hygeia_ai.service_plan_2 import generate_plan

logger = getLogger("uvicorn.app")

def get_form_url_add_new_patient(line_identifier: str) -> str:
    form_url_base = "https://docs.google.com/forms/d/e/1FAIpQLSedKqPBPeqQnP-ty43t--x1DBXcKyKcsBs7B_olOlG10VGTaw/viewform?usp=pp_url&entry.892889867="
    return form_url_base + urllib.parse.quote(line_identifier)


@handler.add(PostbackEvent)
async def handle_postback(event: PostbackEvent) -> None:  # type: ignore[no-any-unimported]
    line_identifier = event.source.user_id
    logger.info(f"PostbackEvent. {line_identifier=}, {event.postback.data=}")


    ##############
    # 状態取得
    user_ref = db.collection("users").document(line_identifier)
    user_info = user_ref.get().to_dict()


    text = event.postback.data

    if text == "create_care_plan":
        user_ref.set({"count_generate_care_plan": firestore.Increment(1), "answers": {
                "question_1": None,
                "question_2": None,
                "question_3": None,
                "question_4": None,
                "question_5": None,
                "question_6": None,
                "question_7": None,
                "question_8": None,
            },
            "state": "wait_q1"}, merge=True)

        await line_bot_api.reply_message(
            ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                TextMessage(text="それでは、いくつか質問をするので回答をお願いします🙏 質問は合計で8つです"),
                TextMessage(text="Q.1 現在、生活の中で特に困っていることや、解決したい課題を教えてください。")
            ],
            )
        )

    if user_info.get("state") == "wait_q3":
        user_ref.set({"answers": {"question_3": text}, "state": "wait_q4"}, merge=True)
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text="Q.4 医師から特定の介護サービスや医療的ケアの指示はありますか？"),
                    FlexMessage(
                        altText="Q.4 医師から特定の介護サービスや医療的ケアの指示はありますか？",
                        contents=generate_list_flex_bubble(labels=[
                            "特に指示なし",
                            "訪問リハビリを受けるように言われている",
                            "訪問看護を勧められている",
                            "嚥下機能の低下があり、誤嚥リスクの管理が必要",
                            "認知症が進行しており、専門的な支援が必要",
                            "その他 (自由入力)",
                        ], text_align="flex-start"),
                    )
                ],
            )
        )

    elif user_info.get("state") == "wait_q4":
        if text == "その他 (自由入力)":
            user_ref.set({"state": "wait_q4_other"}, merge=True)
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text="Q.4 医師からの指示を教えてください。"),
                    ],
                )
            )
        else:
            user_ref.set({"answers": {"question_4": text}, "state": "wait_q5"}, merge=True)
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

    elif user_info.get("state") == "wait_q5":
        if text == "その他 (自由入力)":
            user_ref.set({ "state": "wait_q5_other"}, merge=True)
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text="利用している介護サービスを教えてください。"),
                    ],
                )
            )
        else:
            user_ref.set({"answers": {"question_5": text}, "state": "wait_q6"}, merge=True)
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
    elif user_info.get("state") == "wait_q6":
        if text == "その他 (自由入力)":
            user_ref.set({"state": "wait_q6_other"}, merge=True)
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text="ご自宅の環境について教えてください。"),
                    ],
                )
            )
        else:
            user_ref.set({"answers": {"question_6": text}, "state": "wait_q7"}, merge=True)
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
    elif user_info.get("state") == "wait_q7":
        if text == "その他 (自由入力)":
            user_ref.set({"state": "wait_q7_other"}, merge=True)
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text="介護負担の状況を教えてください。"),
                    ],
                )
            )
        else:
            user_ref.set({"answers": {"question_7": text}, "state": "wait_q8"}, merge=True)
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
    elif user_info.get("state") == "wait_q8":
        user_ref.set({"answers": {"question_8": text}, "state": "wait_gpt"}, merge=True)
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text="回答ありがとうございます。"),
                    TextMessage(text="AIケアプランを作成します。"),
                    TextMessage(text="少々お待ちください。"),
                ],
            )
        )
        await line_bot_api.show_loading_animation(ShowLoadingAnimationRequest(chatId=event.source.user_id))

        answers = user_ref.get().to_dict().get("answers")
        logger.info(f"debug: {answers=}")
        careplan_text = anwer_to_care_planer(openai_client, answers)
        await line_bot_api.push_message(
            PushMessageRequest(to=line_identifier, messages=[TextMessage(text="AIケアプランが作成されました。"), TextMessage(text=careplan_text)])
        )
