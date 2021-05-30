from abc import ABC, abstractmethod
from typing import Any, Optional

import httpx
from httpx import Response, _types


class HttpClientABC(ABC):
    @abstractmethod
    async def get(
        self,
        url: str,
        *,
        params: Optional[_types.QueryParamTypes] = None,
        headers: Optional[_types.HeaderTypes] = None,
        cookies: Optional[_types.CookieTypes] = None,
    ) -> Response:
        ...

    @abstractmethod
    async def post(
        self,
        url: str,
        *,
        params: Optional[_types.QueryParamTypes] = None,
        body: Optional[Any] = None,
        data: Optional[_types.RequestData] = None,
    ) -> Response:
        ...


class HttpClient(HttpClientABC):
    """Обертка над запросами в API."""

    async def get(
        self,
        url: str,
        *,
        params: Optional[_types.QueryParamTypes] = None,
        headers: Optional[_types.HeaderTypes] = None,
        cookies: Optional[_types.CookieTypes] = None,
    ) -> Response:
        """Обертка над get-запросом."""
        async with httpx.AsyncClient() as client:
            return await client.get(url, params=params, headers=headers, cookies=cookies)

    async def post(
        self,
        url: str,
        *,
        params: Optional[_types.QueryParamTypes] = None,
        body: Optional[Any] = None,
        data: Optional[_types.RequestData] = None,
    ) -> Response:
        """Обертка над post-запросом."""
        async with httpx.AsyncClient() as client:
            return await client.post(url, json=body, params=params, data=data)
