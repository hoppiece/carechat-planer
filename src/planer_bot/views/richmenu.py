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

from planer_bot.config import line_bot_api, settings

logger = getLogger("uvicorn.app")


def generate_richmenu() -> RichMenuRequest:
    richmenu_to_create = RichMenuRequest(
        size=RichMenuSize(width=2500, height=843),
        selected=True,
        name="richmenu",
        chatBarText="ケアプラン作成スタート",
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=2500, height=843),
                action=PostbackAction(label="ケアプラン作成", data="create_care_plan"),
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
    logger.info(f"Richmenu updated. {richmenu_id=}")
