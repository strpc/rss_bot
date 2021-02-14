import re
from typing import List
from urllib.parse import urlparse

import feedparser
from pydantic import BaseModel, Field, HttpUrl, ValidationError, validator

from app.project.settings import (COUNT_ARTICLE_UPDATE, COUNT_TEXT_SYMBOL,
                                  COUNT_TITLE_SYMBOL)


class UrlFeed(BaseModel):
    url_feed: HttpUrl = Field(...)


class ListUrls(BaseModel):
    list_urls: List[UrlFeed] = Field(...)

    @validator('list_urls', pre=True, always=True)
    def _validate_urls(cls, input_value: str):
        if not isinstance(input_value, str):
            raise ValueError()
        urls_str = input_value.replace('\n', ' ').replace(',', ' ').lower()
        list_urls = list(set(urls_str.split(' ')))
        urls = []
        for url_ in list_urls:
            if url_:  # был пробел - стал пустая строка
                if not url_.startswith(('http', 'https')):
                    url_ = f'http://{url_}'

                if url_.startswith('https://'):
                    url_ = url_.replace('https://', 'http://')

                if cls.validate_feed(url_):
                    try:
                        urls.append(UrlFeed(url_feed=url_))
                    except ValidationError:
                        pass
        return urls

    @staticmethod
    def validate_feed(url_: str) -> bool:
        """Валидируем, что урл - это фид, а не ссылка на гугл"""
        return bool(feedparser.parse(url_).get('entries'))

    @classmethod
    def get_instance(cls, text: str) -> 'ListUrls':
        return cls(list_urls=text)

    def __iter__(self):
        for elem in self.list_urls:
            yield elem.url_feed

    def __len__(self):
        return len(self.list_urls)


class RssFeed:
    def __init__(self, url: str):
        self.url = url
        self.feed = None

    def parse(self) -> List['Article']:
        self.feed = feedparser.parse(self.url).get('entries')

        articles = []
        for item in self.feed[:COUNT_ARTICLE_UPDATE]:
            articles.append(
                Article(
                    url=item.get('link'),
                    text=item.get('summary'),
                    title=item.get('title')
                )
            )
        return articles


class Article:
    def __init__(self, url: str, text: str, title: str = ''):
        self.url = self._remove_query(url) if url else ''
        self.text = self._remove_tags(text).rstrip() if text else ''
        self.title = self._remove_tags(title) if title else ''

    def __repr__(self):
        return f"{self.url} - {self.title[:COUNT_TITLE_SYMBOL]}... - " \
               f"{self.text[:COUNT_TEXT_SYMBOL]}..."

    @staticmethod
    def _remove_tags(text: str) -> str:
        if not isinstance(text, str):
            return text

        cleanr = re.compile(r'<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        cleantext = re.sub(cleanr, '', text)
        return cleantext.replace('\n', ' ')

    @staticmethod
    def _remove_query(url: str) -> str:
        return urlparse(url)._replace(query='', params='').geturl()
