from typing import List

from pydantic import BaseModel, Field, HttpUrl, ValidationError, validator

from app.core.utils import validate_feed, validate_url


class Feed(BaseModel):
    url: HttpUrl = Field(...)


class ListFeeds(BaseModel):
    feeds: List[Feed] = Field(...)

    @validator("feeds", pre=True, always=True)
    def _validate_feeds(cls, input_value: str):
        if not isinstance(input_value, str):
            raise ValueError

        urls_str = input_value.replace("\n", " ").replace(",", " ").lower()
        list_urls = list(set(urls_str.split(" ")))

        urls = []
        for url in list_urls:
            if not url or validate_url(url) is False:
                continue

            if url.startswith("https://"):
                url = url.replace("https://", "http://")

            if validate_feed(url) is True:
                try:
                    urls.append(Feed(url=url))
                except ValidationError:
                    pass
        return urls

    def __iter__(self):
        for elem in self.feeds:
            yield elem.url

    def __len__(self):
        return len(self.feeds)
