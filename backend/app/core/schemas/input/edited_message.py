from datetime import datetime

from pydantic import BaseModel, Field

from app.core.schemas.input.base import Chat, TypeUpdate, User


class EditedMessageBody(BaseModel):
    message_id: int
    user: User = Field(..., alias="from")
    chat: Chat
    date: datetime
    edit_date: datetime
    text: str


class EditedMessage(BaseModel):
    update_id: int
    edited_message: EditedMessageBody
    type_update: TypeUpdate = TypeUpdate.edited_message
