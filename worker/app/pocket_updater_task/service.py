from loguru import logger

from app.clients.pocket import PocketIntegrationError
from app.pocket.service import PocketService
from app.users.service import UsersService


async def update_access_tokens(
    *,
    pocket_service: PocketService,
    users_service: UsersService,
) -> None:
    request_tokens = await users_service.get_new_request_token()
    if request_tokens is None:
        logger.info("Нет новых request_token-ов")
        return

    logger.info("Новых {} request_token-ов", len(request_tokens))
    logger.debug("Получаем access токены...")
    for request_token in request_tokens:
        logger.debug("Обрабатываем {}...", request_token)

        try:
            access_token = await pocket_service.get_access_token(request_token)
        except PocketIntegrationError as error:
            await users_service.disable_pocket_integration(
                request_token=request_token,
                error_code=error.pocket_error_code,
                error_message=error.pocket_error_message,
                status_code=error.http_status_code,
            )
            continue

        logger.debug("Получили access_token. Обновим его в базе...")
        await users_service.update_access_token(
            request_token=request_token,
            access_token=access_token,  # type: ignore
        )
