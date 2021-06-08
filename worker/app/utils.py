import asyncio


try:
    import contextvars

    contextvars_exists = True
except ImportError:
    contextvars_exists = False

import base64
import functools
from typing import Any, Callable, Union


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
    if contextvars_exists:
        child = functools.partial(func, *args, **kwargs)
        context = contextvars.copy_context()
        func = context.run
        args = (child,)
    elif kwargs:
        func = functools.partial(func, **kwargs)
    return await loop.run_in_executor(None, func, *args)


def safetyed_markdown_text(text: str) -> str:
    new_text = (
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
        .replace("*", "\\*")
        .replace("+", "\\+")
        .replace("!", "\\!")
    )
    return new_text


def bold_markdown(text: str) -> str:
    return f"*{text}*"


def get_hash(*args: Union[str, int]) -> str:
    hash_ = ""
    for i in args:
        if not isinstance(i, (str, int)):
            continue
        hash_ += str(i)
    return base64.b64encode(hash_.encode()).decode()
