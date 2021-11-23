from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional, Union

from app.api.endpoints.update.enums import TypeUpdate
from app.api.endpoints.update.schemas import (
    Callback,
    CallbackIntegrationServicePayload,
    CallbackQuery,
    Message,
)


@dataclass
class Update:
    chat_id: int
    text: str
    command: Optional[str]
    type: TypeUpdate
    payload: Optional[CallbackIntegrationServicePayload]
    message_id: Optional[int]
    callback_query: Optional[CallbackQuery]

    @classmethod
    def from_schema(cls, update: Union[Callback, Message]) -> "Update":
        creators = {
            TypeUpdate.message: cls._from_message,  # type: ignore
            TypeUpdate.callback: cls._from_callback,  # type: ignore
        }
        return creators[update.type_update](update)

    @classmethod
    def _from_message(cls, update: Message) -> "Update":
        return cls(
            chat_id=update.message.chat.id,
            text=update.message.text,
            command=update.message.command,
            type=update.type_update,
            payload=None,
            message_id=None,
            callback_query=None,
        )

    @classmethod
    def _from_callback(cls, update: Callback) -> "Update":
        return cls(
            chat_id=update.callback_query.message.chat.id,
            text=update.callback_query.message.text,
            command=None,
            type=update.type_update,
            payload=update.callback_query.data,
            message_id=update.callback_query.message.message_id,
            callback_query=update.callback_query,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
