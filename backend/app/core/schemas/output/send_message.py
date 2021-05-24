from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel


class ParseMode(str, Enum):
    MarkdownV2 = "MarkdownV2"
    HTML = "HTML"
    Markdown = "Markdown"


class InlineKeyboardButton(BaseModel):
    text: str
    callback_data: Optional[str] = None


class InlineKeyboardMarkup(BaseModel):
    inline_keyboard: List[InlineKeyboardButton]


class SendMessage(BaseModel):
    chat_id: Union[int, str]
    text: str
    parse_mode: Optional[ParseMode] = None
    disable_web_page_preview: Optional[bool] = None
    disable_notification: Optional[bool] = None
    reply_to_message_id: Optional[bool] = None
    allow_sending_without_reply: Optional[bool] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
