import feedparser
from pydantic import BaseModel, HttpUrl, Field, validator

import re
from urllib.parse import urlparse
from typing import Optional, List


class UrlFeed(BaseModel):
    url_feed: HttpUrl = Field(...)


class ListUrls(BaseModel):
    list_urls: List[UrlFeed] = Field(...)

    @validator('list_urls', pre=True, always=True)
    def get_urls(cls, input_value: str):
        if not isinstance(input_value, str):
            raise ValueError()
        urls_str = input_value.replace('\n', ' ').replace(',', ' ')
        urls = []
        for url in urls_str.split(' '):
            if url:  # был пробел - стал пустая строка
                urls.append(UrlFeed(url_feed=url))
        return urls

    def __iter__(self):
        for elem in self.list_urls:
            yield elem.url_feed


class RssFeed(UrlFeed):
    feed: Optional[str] = Field(None)

    @validator('url_feed')
    def run_parse(cls, input_value):
        # cls.parse()
        return input_value

    @staticmethod
    def _remove_tags(text: str) -> str:
        if isinstance(text, str):
            cleanr = re.compile(r'<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
            cleantext = re.sub(cleanr, '', text)
            return cleantext.replace('\n', ' ')
        return text

    def parse(self):
        self.feed = feedparser.parse(self.url_feed).get('entries')

        for item in self.feed:
            for k in item:
                item[k] = self._remove_tags(item[k])

    @staticmethod
    def remove_query(self):
        urlparse(r.feed[0].get('link'))._replace(query='', params='').geturl()

