from typing import Optional, Union

from fastapi import Body, Depends, Request
from loguru import logger

from app.config import MainConfig
from app.core.clients.database import Database
from app.core.clients.http_ import HttpClient
from app.core.clients.telegram import Telegram
from app.core.commands.add_feed.repository import CommandAddFeedRepository
from app.core.commands.add_feed.service import CommandAddFeedService
from app.core.commands.delete_feed.repository import CommandDeleteFeedRepository
from app.core.commands.delete_feed.service import CommandDeleteFeedService
from app.core.commands.list_feed.repository import CommandListFeedRepository
from app.core.commands.list_feed.service import CommandListFeedService
from app.core.commands.start.repository import CommandStartRepository
from app.core.commands.start.service import CommandStartService
from app.core.service_messages.repository import ServiceMessagesRepository
from app.core.service_messages.service import ServiceMessagesService
from app.core.users.models import User
from app.core.users.repository import UsersRepository
from app.core.users.service import UsersService
from app.schemas.message import Message


CommandsServicesType = Union[
    CommandStartService, CommandAddFeedService, CommandListFeedService, CommandDeleteFeedService
]


def get_http_client() -> HttpClient:
    return HttpClient()


def get_config(request: Request) -> MainConfig:
    return request.app.state.config


def get_telegram_client(
    http_client: HttpClient = Depends(get_http_client),
    config: MainConfig = Depends(get_config),
) -> Telegram:
    return Telegram(token=config.telegram.token, client=http_client)


def get_database(request: Request) -> Database:
    return request.app.state.db


def get_service_messages_repository(
    db: Database = Depends(get_database),
) -> ServiceMessagesRepository:
    return ServiceMessagesRepository(database=db)


def get_service_messages_service(
    repository: ServiceMessagesRepository = Depends(get_service_messages_repository),
    telegram: Telegram = Depends(get_telegram_client),
) -> ServiceMessagesService:
    return ServiceMessagesService(repository=repository, telegram=telegram)


def get_command_start_repository(db: Database = Depends(get_database)) -> CommandStartRepository:
    return CommandStartRepository(database=db)


def get_command_start_service(
    repository: CommandStartRepository = Depends(get_command_start_repository),
    telegram: Telegram = Depends(get_telegram_client),
    service_messages: ServiceMessagesService = Depends(get_service_messages_service),
) -> CommandStartService:
    return CommandStartService(
        repository=repository,
        telegram=telegram,
        service_messages=service_messages,
    )


def get_command_add_feed_repository(
    db: Database = Depends(get_database),
) -> CommandAddFeedRepository:
    return CommandAddFeedRepository(database=db)


def get_command_add_feed_service(
    repository: CommandAddFeedRepository = Depends(get_command_add_feed_repository),
    telegram: Telegram = Depends(get_telegram_client),
    service_messages: ServiceMessagesService = Depends(get_service_messages_service),
) -> CommandAddFeedService:
    return CommandAddFeedService(
        repository=repository,
        telegram=telegram,
        service_messages=service_messages,
    )


def get_command_list_feed_repository(
    db: Database = Depends(get_database),
) -> CommandListFeedRepository:
    return CommandListFeedRepository(database=db)


def get_command_list_feed_service(
    repository: CommandListFeedRepository = Depends(get_command_list_feed_repository),
    telegram: Telegram = Depends(get_telegram_client),
    service_messages: ServiceMessagesService = Depends(get_service_messages_service),
) -> CommandListFeedService:
    return CommandListFeedService(
        repository=repository,
        telegram=telegram,
        service_messages=service_messages,
    )


def get_command_delete_feed_repository(
    db: Database = Depends(get_database),
) -> CommandDeleteFeedRepository:
    return CommandDeleteFeedRepository(database=db)


def get_command_delete_feed_service(
    repository: CommandDeleteFeedRepository = Depends(get_command_delete_feed_repository),
    telegram: Telegram = Depends(get_telegram_client),
    service_messages: ServiceMessagesService = Depends(get_service_messages_service),
) -> CommandDeleteFeedService:
    return CommandDeleteFeedService(
        repository=repository,
        telegram=telegram,
        service_messages=service_messages,
    )


def get_users_repository(db: Database = Depends(get_database)) -> UsersRepository:
    return UsersRepository(database=db)


def get_users_service(
    users_repository: UsersRepository = Depends(get_users_repository),
) -> UsersService:
    return UsersService(repository=users_repository)


async def get_current_user(
    users_service: UsersService = Depends(get_users_service),
    update: Message = Body(...),
) -> User:
    user = await users_service.get_or_create(update)
    if not user.active:
        logger.info("Юзер найден, но не активен.")
        await users_service.activate_user(user.chat_id)
    return user


def get_command_service(
    update: Message = Body(...),
    command_start_service: CommandStartService = Depends(get_command_start_service),
    command_add_feed_service: CommandStartService = Depends(get_command_add_feed_service),
    command_list_feed_service: CommandStartService = Depends(get_command_list_feed_service),
    command_delete_feed_service: CommandStartService = Depends(get_command_delete_feed_service),
) -> Optional[CommandsServicesType]:
    commands_map = {
        "start": command_start_service,
        "add_feed": command_add_feed_service,
        "list_feed": command_list_feed_service,
        "delete_feed": command_delete_feed_service,
    }
    return commands_map.get(update.message.command)  # type: ignore  # FIXME
