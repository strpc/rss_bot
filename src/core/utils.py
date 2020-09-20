from datetime import datetime
from typing import Optional, List, Union
import base64

from src.core.schemas.rss import ListUrls


def from_timestamp(unixtime: Optional[int] = None) -> Optional[datetime]:
    if unixtime is None:
        return None
    return datetime.fromtimestamp(unixtime)


def make_hash(*args) -> str:
    hash_ = ''
    for i in args:
        if not isinstance(i, (str, int)):
            continue
        hash_ += str(i)
    return base64.b64encode(hash_.encode()).decode()


def make_str_urls(urls: Union[List, ListUrls]) -> str:
    return '\n'.join(urls)
