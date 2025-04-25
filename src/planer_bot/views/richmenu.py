from logging import getLogger
from pathlib import Path

import requests
from linebot.v3.messaging.models import (  # type: ignore
    PostbackAction,
    RichMenuArea,
    RichMenuBounds,
    RichMenuRequest,
    RichMenuSize,
)

from planer_bot.config import db, line_bot_api, settings

logger = getLogger("uvicorn.app")


def generate_richmenu() -> RichMenuRequest:
    richmenu_to_create = RichMenuRequest(
        size=RichMenuSize(width=2500, height=843),
        selected=True,
        name="richmenu",
        chatBarText="ケアプラン作成スタート",
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=1250, height=843),
                action=PostbackAction(
                    label="ケアプラン作成",
                    data="create_care_plan",
                    displayText="最初からケアプラン作成",
                ),
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=1250, y=0, width=1250, height=843),
                action=PostbackAction(
                    label="ケアマネ秘書",
                    data="secretary",
                    inputOption="openKeyboard",
                    displayText="ケアマネ秘書",
                ),
            ),
        ],
    )
    return richmenu_to_create


def upload_richmenu_image(
    richmenu_id: str,
    image_path: Path | str,
    content_type: str = "image/png",
) -> requests.Response:
    url = f"https://api-data.line.me/v2/bot/richmenu/{richmenu_id}/content"
    channel_access_token = settings.LINE_CHANNEL_ACCESS_TOKEN
    headers = {
        "Authorization": f"Bearer {channel_access_token}",
        "Content-Type": content_type,
    }
    with open(image_path, "rb") as f:
        response = requests.post(url, headers=headers, data=f)
    return response


async def update_richmenu() -> None:
    # Delete the existing richmenu
    existing_richmenus = await line_bot_api.get_rich_menu_list()
    for richmenu in existing_richmenus.richmenus:
        await line_bot_api.delete_rich_menu(richmenu.rich_menu_id)

    # Create a new richmenu
    richmenu_response = await line_bot_api.create_rich_menu(generate_richmenu())
    richmenu_id = richmenu_response.rich_menu_id

    path = Path(__file__).parent / "data/richmenu.png"
    upload_richmenu_image(richmenu_id, path)
    await line_bot_api.set_default_rich_menu(richmenu_id)

    db.collection("settings").document("richmenu").set({"richmenu_id": richmenu_id})
    logger.info(f"Richmenu updated. {richmenu_id=}")


async def get_default_richmenu_id() -> str:
    doc = db.collection("settings").document("richmenu").get().to_dict() or {}
    richmenu_id = doc.get("richmenu_id")
    if not richmenu_id:
        await update_richmenu()
        doc = db.collection("settings").document("richmenu").get().to_dict() or {}
        richmenu_id = doc.get("richmenu_id")
        if not richmenu_id:
            raise ValueError("richmenu_idが設定されていません")
    return richmenu_id


def link_rich_menu_to_user(line_identifier: str, rich_menu_id: str) -> None:
    url = f"https://api.line.me/v2/bot/user/{line_identifier}/richmenu/{rich_menu_id}"
    headers = {
        "Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}",
    }
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error linking rich menu: {response.text}")
