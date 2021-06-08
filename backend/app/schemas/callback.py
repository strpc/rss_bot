from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.enums import TypeUpdate


class User(BaseModel):
    id: int
    is_bot: bool
    first_name: Optional[str]
    username: Optional[str]
    language_code: Optional[str]


class BotInfo(BaseModel):
    id: int
    is_bot: bool
    first_name: Optional[str]
    username: Optional[str]


class ChatInfo(BaseModel):
    id: int
    first_name: Optional[str]
    username: Optional[str]
    type: Optional[str]


class Message(BaseModel):
    message_id: int
    from_bot: BotInfo = Field(alias="from")
    chat: ChatInfo
    date: int
    text: str
    entities: List[Dict]
    reply_markup: Dict


class CallbackQuery(BaseModel):
    id: int
    user: User = Field(alias="from")
    message: Message
    chat_instance: str
    type_update: TypeUpdate = TypeUpdate.callback
    data: Optional[str] = None


class Callback(BaseModel):
    update_id: int
    callback_query: CallbackQuery
    type_update: TypeUpdate = TypeUpdate.callback
