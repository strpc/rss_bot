import asyncio
import functools
from typing import Any, Callable

from easy_notifyer import telegram_reporter as _telegram_reporter

from app.config import get_config


def empty_decorator(*args: Any, **kwargs: Any) -> Callable:  # noqa
    def decorator(*args: Any, **kwargs: Any) -> Callable:  # noqa
        def wrapped(func: Callable) -> Callable:
            def sync_wrapped(*args: Any, **kwargs: Any) -> Any:  # noqa
                return func(*args, **kwargs)

            async def async_wrapped(*args: Any, **kwargs: Any) -> Any:  # noqa
                return await func(*args, **kwargs)

            if asyncio.iscoroutinefunction(func):
                return functools.wraps(func)(async_wrapped)
            return functools.wraps(func)(sync_wrapped)

        return wrapped

    return decorator


def get_telegram_reporter() -> Callable:
    config = get_config()
    if config.app.debug:
        return empty_decorator()
    return _telegram_reporter(
        token=config.easy_notifyer.token,
        chat_id=config.easy_notifyer.chat_id,
        service_name=config.easy_notifyer.service_name,
    )


telegram_reporter = get_telegram_reporter()
