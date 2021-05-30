from typing import Optional

from pydantic import BaseModel, Field


class Feed(BaseModel):
    url: str
    chat_id_url_hash: str


class Entry(BaseModel):
    url: Optional[str] = Field(alias="link")
    text: Optional[str] = Field(alias="summary")
    title: Optional[str] = Field(alias="title")
