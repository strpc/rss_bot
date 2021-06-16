import asyncio
import base64
import contextvars
import functools
from typing import Any, Callable, Union
from urllib.parse import urlparse

from loguru import logger


def get_hash(*args: Union[str, int]) -> str:
    hash_ = ""
    for i in args:
        if not isinstance(i, (str, int)):
            continue
        hash_ += str(i)
    return base64.b64encode(hash_.encode()).decode()


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


def safetyed_markdown_text(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("{", "\\{")
        .replace("}", "\\}")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .replace(">", "\\>")
        .replace("<", "\\<")
        .replace("`", "\\`")
        .replace(".", "\\.")
        .replace("#", "\\#")
        .replace("_", "\\_")
        .replace("-", "\\-")
        .replace("=", "\\=")
        .replace("*", "\\*")
        .replace("+", "\\+")
        .replace("!", "\\!")
        .replace("|", "\\|")
    )


def bold_markdown(text: str) -> str:
    return f"*{text}*"
