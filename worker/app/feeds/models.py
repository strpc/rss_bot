import re
from typing import Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, validator


class Feed(BaseModel):
    url: str
    chat_id_url_hash: str


class Entry(BaseModel):
    url: Optional[str] = Field(alias="link")
    text: Optional[str] = Field(alias="summary")
    title: Optional[str] = Field(alias="title")

    @validator("text")
    def remove_tags(cls, value: Optional[str]) -> Optional[str]:
        print(type(value))
        if isinstance(value, str):
            cleanr = re.compile(r"<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
            cleantext = re.sub(cleanr, "", value)
            return cleantext.replace("\n", " ")
        return value

    @validator("url")
    def remove_query(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            return urlparse(value)._replace(query="", params="").geturl()
        return value


class UserEntry(BaseModel):
    id: int
    title: Optional[str]
    url: Optional[str]
    text: Optional[str]
    chat_id: int
