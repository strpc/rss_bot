from datetime import datetime
from typing import Optional, List


def from_timestamp(unixtime: Optional[int] = None) -> Optional[datetime]:
    if unixtime is None:
        return None
    return datetime.fromtimestamp(unixtime)


def list_urls(urls: str) -> List[str]:
    pass
