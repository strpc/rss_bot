from loguru import logger

from app.core.clients.pocket import PocketClient, PocketError
from app.core.integration.pocket import PocketIntegration


async def update_access_tokens(
    *,
    pocket_client: PocketClient,
    pocket_integration: PocketIntegration,
) -> None:
    request_tokens = await pocket_integration.get_new_request_token()
    if request_tokens is None:
        logger.info("Нет новых request_token-ов")
        return

    logger.info("Новых {} request_token-ов", len(request_tokens))
    logger.debug("Получаем access токены...")
    for item in request_tokens:
        logger.debug("Обрабатываем {}...", item)

        try:
            access_token = await pocket_client.get_access_token(
                item["pocket_request_token"],
            )
        except PocketError as error:
            await pocket_integration.disable_pocket_integration(
                user_id=item["user_id"],
                error_code=error.pocket_error_code,
                error_message=error.pocket_error_message,
                status_code=error.http_status_code,
            )
            continue

        logger.info("Получили access_token. Обновим его в базе...")
        await pocket_integration.update_access_token(
            user_id=item["user_id"],
            access_token=access_token,  # type: ignore
        )
