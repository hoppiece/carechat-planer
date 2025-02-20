import urllib.parse
from logging import getLogger

from jinja2 import Environment, FileSystemLoader
from linebot.v3.messaging import (  # type: ignore
    FlexMessage,
    PushMessageRequest,
    ReplyMessageRequest,
    ShowLoadingAnimationRequest,
    TextMessage,
)
from linebot.v3.webhooks import PostbackEvent  # type: ignore

from planer_bot import models
from planer_bot.config import db, handler, line_bot_api, openai_client
from planer_bot.views.flexmessage_list import generate_list_flex_bubble

# from hygeia_ai.service_plan_2 import generate_plan

logger = getLogger("uvicorn.app")
gpt_template = Environment(loader=FileSystemLoader(".")).get_template("careplan_prompt.j2")

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
    if user_info.get("state") == "wait_q3":
        user_ref.update({"answers.question_3": text, "state": "wait_q4"})
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
            user_ref.update({"state": "wait_q4_other"})
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text="Q.4 医師からの指示を教えてください。"),
                    ],
                )
            )
        else:
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

    elif user_info.get("state") == "wait_q5":
        if text == "その他 (自由入力)":
            user_ref.update({ "state": "wait_q5_other"})
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text="利用している介護サービスを教えてください。"),
                    ],
                )
            )
        else:
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
    elif user_info.get("state") == "wait_q6":
        if text == "その他 (自由入力)":
            user_ref.update({"state": "wait_q6_other"})
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text="ご自宅の環境について教えてください。"),
                    ],
                )
            )
        else:
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
    elif user_info.get("state") == "wait_q7":
        if text == "その他 (自由入力)":
            user_ref.update({"state": "wait_q7_other"})
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text="介護負担の状況を教えてください。"),
                    ],
                )
            )
        else:
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
    elif user_info.get("state") == "wait_q8":
        user_ref.update({"answers.question_8": text, "state": "wait_gpt"})
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
        system_prompt = gpt_template.render()
        user_input = "\n".join(
            [f"{key}: {value}" for key, value in answers.items()]
        )
        completion = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": user_input,
                }
            ]
        )
        careplan_text = completion.choices[0].message.content
        await line_bot_api.push_message(
            PushMessageRequest(to=line_identifier, messages=[TextMessage(text="AIケアプランが作成されました。"), TextMessage(text=careplan_text)])
        )
