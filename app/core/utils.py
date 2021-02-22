import base64
from datetime import datetime
from typing import Iterable, Optional
from urllib.parse import urlparse

import feedparser


def from_timestamp(unixtime: Optional[int] = None) -> Optional[datetime]:
    if unixtime is None:
        return None
    return datetime.fromtimestamp(unixtime)


def get_hash(*args) -> str:
    hash_ = ""
    for i in args:
        if not isinstance(i, (str, int)):
            continue
        hash_ += str(i)
    return base64.b64encode(hash_.encode()).decode()


def make_str_urls(urls: Iterable[str]) -> str:
    return "\n".join(urls)


def validate_feed(url: str) -> bool:
    return bool(feedparser.parse(url).get("entries"))


def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])
