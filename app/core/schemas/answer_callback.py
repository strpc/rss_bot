from typing import Optional

from pydantic import BaseModel


class AnswerCallback(BaseModel):
    callback_query_id: str
    text: Optional[str] = None
