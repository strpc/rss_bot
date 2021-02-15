from typing import Optional

from pydantic import BaseModel, Field

from app.core.schemas.input.base import TypeUpdate, User
from app.core.schemas.input.message import MessageBody


class Callback(BaseModel):
    id: str
    user: User = Field(..., alias='from')
    message: Optional[MessageBody] = None
    inline_message_id: Optional[str] = None
    data: Optional[str] = None
    type_update: TypeUpdate = TypeUpdate.callback
