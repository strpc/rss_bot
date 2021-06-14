import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from app.schemas.enums import ServiceIntegration, TypeUpdate


class CallbackIntegrationServicePayload(BaseModel):
    service: ServiceIntegration
    entry_id: int
    sended: bool


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


class Button(BaseModel):
    text: str
    callback_data: CallbackIntegrationServicePayload

    @validator("callback_data", pre=True, always=True)
    def validate_callback_data(cls, value: Any) -> Optional[CallbackIntegrationServicePayload]:
        if not isinstance(value, str):
            raise ValueError(f"value={value}")
        callback_data = json.loads(value)
        return CallbackIntegrationServicePayload(**callback_data)


class InlineKeyboard(BaseModel):
    inline_keyboard: List[List[Button]]


class Message(BaseModel):
    message_id: int
    from_bot: BotInfo = Field(alias="from")
    chat: ChatInfo
    date: int
    text: str
    entities: List[Dict]
    reply_markup: InlineKeyboard


class CallbackQuery(BaseModel):
    id: int
    user: User = Field(alias="from")
    message: Message
    chat_instance: str
    type_update: TypeUpdate = TypeUpdate.callback
    data: Optional[CallbackIntegrationServicePayload] = None

    @validator("data", pre=True, always=True)
    def validate_callback_data(cls, value: Any) -> Optional[CallbackIntegrationServicePayload]:
        if not isinstance(value, str):
            raise ValueError(f"value={value}")
        callback_data = json.loads(value)
        return CallbackIntegrationServicePayload(**callback_data)


class Callback(BaseModel):
    update_id: int
    callback_query: CallbackQuery
    type_update: TypeUpdate = TypeUpdate.callback
