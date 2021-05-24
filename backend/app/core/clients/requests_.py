import logging
from abc import ABC, abstractmethod
from time import sleep
from typing import Dict

import httpx
from app.project.settings import ATTEMPT_REQUEST, DELAY_REQUEST


logger = logging.getLogger(__name__)


class IRequests(ABC):
    @abstractmethod
    def get(self, method: str, params: Dict, attempt=ATTEMPT_REQUEST):
        ...

    @abstractmethod
    def post(self, url: str, params=None, body=None, data=None, attempt=ATTEMPT_REQUEST):
        ...


class Requests(IRequests):
    """Обертка над запросами в API"""

    def get(self, url: str, params: Dict, attempt=ATTEMPT_REQUEST) -> httpx.Response:
        """Обертка над get-запросом"""
        response = httpx.get(url, params=params)

        if response.status_code != 200 and attempt:
            sleep(DELAY_REQUEST)
            attempt -= 1
            self.get(url, params, attempt)

        else:
            logger.error(
                "Request error. url: %s. params: %s, status_code: %s, response: %s",
                url,
                params,
                response.status_code,
                response.json(),
            )
        return response

    def post(
        self, url: str, params=None, body=None, data=None, attempt=ATTEMPT_REQUEST
    ) -> httpx.Response:
        """Обертка над post-запросом"""
        response = httpx.post(url, json=body, params=params, data=data)
        if response.status_code == 200:
            return response

        if (  # !ВОПРОСЫ
            response.status_code != 200
            and response.json().get("description") != "Forbidden: bot was blocked by the user"
            and attempt
        ):
            sleep(DELAY_REQUEST)
            attempt -= 1
            return self.post(url, params, body, data, attempt)

        logger.error(
            "Post request error. url: %s. params: %s, body: %s, data: %s, status_code: %s, "
            "response: %s",
            url,
            params,
            body,
            bool(data),
            response.status_code,
            response.json(),
        )
        return response
