from app.config import MainConfig
from app.core.clients.http_ import HttpClient
from app.core.clients.telegram import Telegram
from fastapi import Depends, Request


def get_http_client() -> HttpClient:
    return HttpClient()


def get_config(request: Request) -> MainConfig:
    return request.state.config


def get_telegram(
    http_client: HttpClient = Depends(get_http_client),
    config: MainConfig = Depends(get_config),
) -> Telegram:
    return Telegram(token=config.telegram.token, client=http_client)
