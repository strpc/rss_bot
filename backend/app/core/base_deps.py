from fastapi import Depends, Request

from app.config import MainConfig
from app.core.clients.database import Database
from app.core.clients.http_ import HttpClient
from app.core.clients.telegram import Telegram


def get_config(request: Request) -> MainConfig:
    return request.app.state.config


def get_http_client() -> HttpClient:
    return HttpClient()


def get_telegram_client(
    http_client: HttpClient = Depends(get_http_client),
    config: MainConfig = Depends(get_config),
) -> Telegram:
    return Telegram(token=config.telegram.token, client=http_client)


def get_database(request: Request) -> Database:
    return request.app.state.db
