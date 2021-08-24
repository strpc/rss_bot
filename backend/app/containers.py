import functools

from aiocache import Cache
from dependency_injector import containers, providers

from app.core.callbacks.service import CallbackService
from app.core.clients.database import Database
from app.core.clients.http_ import HttpClient
from app.core.clients.pocket import PocketClient
from app.core.clients.telegram import Telegram
from app.core.commands.add_feed.service import CommandAddFeedService
from app.core.commands.authorize.service import AuthorizeService
from app.core.commands.authorize_pocket.repository import PocketAuthRepository
from app.core.commands.authorize_pocket.service import AuthorizePocketService
from app.core.commands.delete_feed.service import CommandDeleteFeedService
from app.core.commands.list_feed.service import CommandListFeedService
from app.core.commands.start.service import CommandStartService
from app.core.feeds.repository import FeedsRepository
from app.core.feeds.service import FeedsService
from app.core.integration.pocket import PocketIntegration
from app.core.integration.service import ExternalServices
from app.core.service_messages.repository import InternalMessagesRepository
from app.core.service_messages.service import InternalMessagesService
from app.core.users.repository import UsersRepository
from app.core.users.service import UsersService


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    database = providers.Singleton(Database, url=config.db.dsn)
    http_client = providers.Singleton(HttpClient)
    telegram_client = providers.Singleton(
        Telegram,
        token=config.telegram.token,
        client=http_client,
    )
    pocket_client = providers.Singleton(
        PocketClient,
        http_client=http_client,
        consumer_key=config.pocket.consumer_key,
        redirect_url=config.pocket.redirect_url,
    )

    _users_repository = providers.Factory(UsersRepository, database=database)
    users_service = providers.Factory(UsersService, repository=_users_repository)

    _internal_messages_repository = providers.Factory(
        InternalMessagesRepository,
        database=database,
        cache=functools.partial(Cache, cache_class=Cache.MEMORY),
    )
    internal_messages_service = providers.Factory(
        InternalMessagesService,
        telegram=telegram_client,
        repository=_internal_messages_repository,
    )

    _feeds_repository = providers.Factory(
        FeedsRepository,
        database=database,
    )
    feeds_service = providers.Factory(FeedsService, repository=_feeds_repository)

    command_start_service = providers.Factory(
        CommandStartService,
        telegram=telegram_client,
        internal_messages_service=internal_messages_service,
    )

    add_feed_service = providers.Factory(
        CommandAddFeedService,
        feeds_service=feeds_service,
        telegram=telegram_client,
        internal_messages_service=internal_messages_service,
        limit_feed=config.limits.count_feed_user,
    )

    list_feed_service = providers.Factory(
        CommandListFeedService,
        feeds_service=feeds_service,
        telegram=telegram_client,
        internal_messages_service=internal_messages_service,
    )

    delete_feed_service = providers.Factory(
        CommandDeleteFeedService,
        feeds_service=feeds_service,
        telegram=telegram_client,
        internal_messages_service=internal_messages_service,
    )

    authorize_service = providers.Factory(
        AuthorizeService,
        telegram=telegram_client,
        internal_messages_service=internal_messages_service,
    )

    _pocket_auth_repository = providers.Factory(
        PocketAuthRepository,
        database=database,
    )
    authorize_pocket_service = providers.Factory(
        AuthorizePocketService,
        telegram=telegram_client,
        pocket_client=pocket_client,
        repository=_pocket_auth_repository,
        internal_messages_service=internal_messages_service,
    )

    pocket_integration = providers.Factory(
        PocketIntegration,
        pocket_client=pocket_client,
        users_service=users_service,
    )

    external_services = providers.Factory(
        ExternalServices,
        pocket_integration=pocket_integration,
    )

    callback_service = providers.Factory(
        CallbackService,
        users_service=users_service,
        external_services=external_services,
        internal_messages_service=internal_messages_service,
        telegram=telegram_client,
    )
