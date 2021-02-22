import re
from collections.abc import Iterator
from urllib.parse import urlparse

import feedparser

from app.project.settings import COUNT_TEXT_SYMBOL, COUNT_TITLE_SYMBOL


class Article:
    def __init__(self, url: str, text: str, title: str = ""):
        self.url = self._remove_query(url) if url else ""
        self.text = self._remove_tags(text).rstrip() if text else ""
        self.title = self._remove_tags(title) if title else ""

    def __repr__(self):
        return (
            f"{self.url} - {self.title[:COUNT_TITLE_SYMBOL]}... - "
            f"{self.text[:COUNT_TEXT_SYMBOL]}..."
        )

    @staticmethod
    def _remove_tags(text: str) -> str:
        if not isinstance(text, str):
            return text

        cleanr = re.compile(r"<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
        cleantext = re.sub(cleanr, "", text)
        return cleantext.replace("\n", " ")

    @staticmethod
    def _remove_query(url: str) -> str:
        return urlparse(url)._replace(query="", params="").geturl()


class Feed:
    def __init__(self, url: str):
        self.url = url
        self.feed = None

    def parse(self, limit: int) -> Iterator[Article]:
        self.feed = feedparser.parse(self.url).get("entries")
        for item in self.feed[:limit]:
            article = Article(
                url=item.get("link"),
                text=item.get("summary"),
                title=item.get("title"),
            )
            yield article
