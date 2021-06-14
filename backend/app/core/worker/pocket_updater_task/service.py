from loguru import logger

from app.core.clients.pocket import PocketClient, PocketError
from app.core.users.service import UsersService


async def update_access_tokens(
    *,
    pocket_client: PocketClient,
    users_service: UsersService,
) -> None:
    request_tokens = await users_service.get_new_request_token()
    if request_tokens is None:
        logger.info("Нет новых request_token-ов")
        return

    logger.info("Новых {} request_token-ов", len(request_tokens))
    logger.debug("Получаем access токены...")
    for item in request_tokens:
        logger.debug("Обрабатываем {}...", item)

        try:
            access_token = await pocket_client.get_access_token(item["pocket_request_token"])
        except PocketError as error:
            await users_service.disable_pocket_integration(
                user_id=item["user_id"],
                error_code=error.pocket_error_code,
                error_message=error.pocket_error_message,
                status_code=error.http_status_code,
            )
            continue

        logger.debug("Получили access_token. Обновим его в базе...")
        await users_service.update_access_token(
            user_id=item["user_id"],
            access_token=access_token,  # type: ignore
        )
