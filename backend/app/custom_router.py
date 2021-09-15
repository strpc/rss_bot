import time
from typing import Callable, Dict, Tuple
from uuid import uuid4

from fastapi import Request, Response
from fastapi.routing import APIRoute
from loguru import logger


class LoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            body = await request.json()
            logger.debug(body)

            chat_id, username, uuid = self._get_body_values(body)
            before = time.time()
            with logger.contextualize(chat_id=chat_id, username=username, uuid=uuid):
                response: Response = await original_route_handler(request)
                duration = time.time() - before
                logger.debug("Время на обработку запроса составило {} сек", round(duration, 4))
                return response

        return custom_route_handler

    @staticmethod
    def _get_body_values(body: Dict) -> Tuple[int, str, str]:
        chat_id = None
        username = None
        message = body.get("message")
        if message is None:
            callback_query = body.get("callback_query")
            if callback_query is not None:
                message = callback_query.get("message")

        if message is not None:
            chat = message.get("chat")
            if chat is not None:
                chat_id = chat["id"]
                username = chat.get("username", "")

        chat_id = chat_id or 0
        username = username or ""
        uuid = str(uuid4())

        return chat_id, username, uuid
