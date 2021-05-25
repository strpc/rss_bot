import base64
from datetime import datetime
from typing import Iterable, Optional
from urllib.parse import urlparse

import feedparser


def shielding_markdown_text(text: str) -> str:
    new_text = (
        text.replace("_", "\\_")
        .replace("*", "\\*")
        .replace("[", "\\[")
        .replace("`", "\\`")
        .replace(".", "\\.")
    )
    return new_text


def bold_markdown(text: str) -> str:
    return f"*{text}*"


def get_hash(*args) -> str:
    hash_ = ""
    for i in args:
        if not isinstance(i, (str, int)):
            continue
        hash_ += str(i)
    return base64.b64encode(hash_.encode()).decode()


def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])


# todo: ну вот хз нужно ли то, что ниже


def from_timestamp(unixtime: Optional[int] = None) -> Optional[datetime]:
    if unixtime is None:
        return None
    return datetime.fromtimestamp(unixtime)


def make_str_urls(urls: Iterable[str]) -> str:
    return "\n".join(urls)


def validate_feed(url: str) -> bool:
    return bool(feedparser.parse(url).get("entries"))
