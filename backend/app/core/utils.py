import asyncio
import contextvars
import functools
import re
from typing import Any, Callable
from urllib.parse import urlparse

from loguru import logger


ESCAPE_MARKDOWN_PATTERN = re.compile(r"([_*\[\]()~`>#+\-=|{}.!\\])")


def validate_url(url: str) -> bool:
    logger.debug("Провалидируем url {} ...", url)
    parsed_url = urlparse(url)
    if all([parsed_url.scheme, parsed_url.netloc, parsed_url.path]):
        logger.debug("URL валиден. {} - {}", url, parsed_url)
        return True
    logger.warning("URL невалиден. {} - {}", url, parsed_url)
    return False


async def run_in_threadpool(func: Callable, *args: Any, **kwargs: Any) -> Any:
    """
    Run sync func in async code in thread pool.
    Args:
        func(callable): func to run
        *args:
        **kwargs:
    Returns:
        same as func
    """
    loop = asyncio.get_event_loop()
    child = functools.partial(func, *args, **kwargs)
    context = contextvars.copy_context()
    func = context.run
    args = (child,)
    if kwargs:
        func = functools.partial(func, **kwargs)
    return await loop.run_in_executor(None, func, *args)


def escape_md(text: str) -> str:
    return ESCAPE_MARKDOWN_PATTERN.sub(repl=r"\\\1", string=text)


def bold_markdown(text: str) -> str:
    return f"*{text}*"
