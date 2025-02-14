from enum import Enum

from pydantic import BaseModel


class BotAction(Enum):
    richmenu_最初から = "richmenu_最初から"

    postback_要介護選択 = "postback_要介護選択"


class PostBackActionData(BaseModel):
    action_id: BotAction
    
    class Config:
        use_enum_values = True
