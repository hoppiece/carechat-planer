from logging import getLogger
from linebot.v3.webhooks import PostbackEvent, MessageEvent  # type: ignore
from firebase_admin import firestore  # type: ignore
from planer_bot.config import db, line_bot_api, openai_client
from linebot.v3.messaging import (
    ReplyMessageRequest,  # type: ignore
    TextMessage,
    FlexMessage,
    ShowLoadingAnimationRequest,
    PushMessageRequest,
)
from planer_bot.views.flexmessage_list import generate_list_flex_bubble
from planer_bot.gpt import answer_to_care_planer

logger = getLogger("uvicorn.app")


async def process_care_plan(event: PostbackEvent | MessageEvent) -> int:
    line_identifier = event.source.user_id
    user_ref = db.collection("users").document(line_identifier)
    user_info = user_ref.get().to_dict()
    user_state = user_info.get("state")

    if isinstance(event, MessageEvent):
        user_answer = event.message.text
        postback_data = None

    elif isinstance(event, PostbackEvent):
        user_answer = event.postback.data
        postback_data = event.postback.data

    if postback_data == "create_care_plan":
        # 「最初からケアプラン作成」をタップした場合
        # User state の初期化と、最初の質問の提示

        user_ref.set(
            {
                "count_generate_care_plan": firestore.Increment(1),
                "answers": {
                    "question_1": None,
                    "question_2": None,
                    "question_3": None,
                    "question_4": None,
                    "question_5": None,
                    "question_6": None,
                    "question_7": None,
                    "question_8": None,
                    "question_9": None,
                },
                "state": "wait_q1",
            },
            merge=True,
        )

        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="それでは、いくつか質問をするので回答をお願いします🙏 質問は合計で9つです"
                    ),
                    TextMessage(text="Q.1 現在の要介護度を選択してください。"),
                    FlexMessage(
                        altText="Q.1 現在の要介護度を選択してください。",
                        contents=generate_list_flex_bubble(
                            labels=[
                                "要介護1",
                                "要介護2",
                                "要介護3",
                                "要介護4",
                                "要介護5",
                                "申請中 / 不明",
                            ],
                            input_option="openKeyboard",
                        ),
                    ),
                ],
            )
        )

    elif user_state == "wait_q1":
        user_ref.set(
            {"answers": {"question_1": user_answer}, "state": "wait_q2"}, merge=True
        )
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="Q.2 医師からの介護サービスや医療的ケアの指示、健康状態について教えてください。\n"
                        "現状の疾患や既往歴に関しても具体的に記載して下さい"
                    ),
                ],
            )
        )

    elif user_state == "wait_q2":
        user_ref.set(
            {"answers": {"question_2": user_answer}, "state": "wait_q3"}, merge=True
        )
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="Q.3 食事について、最近の様子を教えてください。\n\n"
                        "【例】\n•1日3食食べられているが嚥下が難しくなっている。\n"
                        "•口腔内の問題等もあり（歯周病・義歯・乾燥・痛みなど)"
                    ),
                ],
            )
        )

    elif user_state == "wait_q3":
        user_ref.set(
            {"answers": {"question_3": user_answer}, "state": "wait_q4"}, merge=True
        )
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="Q.4 トイレや入浴について、最近の様子を教えてください。\n\n"
                        "【例】\n•自力でトイレに行ける / 失禁が増えている / 便秘・頻尿あり / オムツ使用\n"
                        "•自力で入浴できる / 介助があれば可能 /入浴の頻度が減っている\n"
                        "•乾燥・かゆみがある / 床ずれが発生している"
                    ),
                ],
            )
        )

    elif user_state == "wait_q4":
        user_ref.set(
            {"answers": {"question_4": user_answer}, "state": "wait_q5"}, merge=True
        )
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="Q.5 ご本人の物忘れや会話、外出について気になることはありますか？\n\n"
                        "【例】\n•物忘れが増えている\n•外出や人と話す機会が減っている"
                    ),
                ],
            )
        )

    elif user_state == "wait_q5":
        user_ref.set(
            {"answers": {"question_5": user_answer}, "state": "wait_q6"}, merge=True
        )
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="Q.6 その他に現在、生活の中で困っていることは何ですか?\n\n"
                        "【例】\n•歩行がつらくなり、デイサービスの利用が大変\n"
                        "•トイレに間に合わず失敗が増えた\n•最近、食事の量が減っている"
                    ),
                ],
            )
        )

    elif user_state == "wait_q6":
        user_ref.set(
            {"answers": {"question_6": user_answer}, "state": "wait_q7"}, merge=True
        )
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="Q.7 家族の介護負担や居住環境について教えてください。\n\n"
                        "【例】\n•本人が独居 / 家族（同居）が主に介護 / 家族（別居）が定期的に介護\n"
                        "•夜間の介護負担が大きい / 仕事と介護の両立が難しい / 食事・排泄介助が負担\n"
                        ""
                        "•段差が多い / トイレ・浴室が使いづらい / 車椅子移動が困難"
                    ),
                ],
            )
        )

    elif user_state == "wait_q7":
        user_ref.set(
            {"answers": {"question_7": user_answer}, "state": "wait_q8"}, merge=True
        )
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="Q.8 現在利用中のサービスを選択してください\n\n"
                        "【例】\nデイサービス週１ / 訪問介護週２ / 福祉用具貸与○○"
                    ),
                ],
            )
        )

    elif user_state == "wait_q8":
        user_ref.set(
            {"answers": {"question_8": user_answer}, "state": "wait_q9"}, merge=True
        )
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="Q.9 今後の生活や介護について、ご本人やご家族の希望を教えてください。\n\n"
                        "【例】\n"
                        "•できるだけ自宅で生活を続けたいので夜間や食事のサポートがほしい\n"
                        "•本人は希望してないが、家族は施設入所を検討している"
                    ),
                ],
            )
        )

    elif user_state == "wait_q9":
        user_ref.set(
            {"answers": {"question_9": user_answer}, "state": "wait_care_plan"},
            merge=True,
        )

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
        await line_bot_api.show_loading_animation(
            ShowLoadingAnimationRequest(chatId=event.source.user_id)
        )

        answers = user_ref.get().to_dict().get("answers")
        logger.info(f"debug: {answers=}")
        careplan_text = answer_to_care_planer(openai_client, answers)

        query_log = {
            "timestamp": firestore.SERVER_TIMESTAMP,
            "answers": answers,
            "careplan": careplan_text,
        }
        db.collection("careplan_query_log").add(query_log)

        await line_bot_api.push_message(
            PushMessageRequest(
                to=line_identifier,
                messages=[
                    TextMessage(text="AIケアプランが作成されました。"),
                    TextMessage(text=careplan_text),
                ],
            )
        )
    return 0
