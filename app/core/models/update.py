import logging
import re
from typing import Optional

from pydantic import BaseModel

from app.core.models.type_update import TypeUpdate

logger = logging.getLogger(__name__)
command_compile = re.compile(r'(^|\s)\/\b[a-zA-Z_]+\b')


class Message(BaseModel):
    chat_id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    text: str
    type_update: TypeUpdate = TypeUpdate.message
    command: Optional[str] = None

    def validate_text(self):  # todo: сделать валидатор команды. и обновление type_update, если команда найдена
        pass
