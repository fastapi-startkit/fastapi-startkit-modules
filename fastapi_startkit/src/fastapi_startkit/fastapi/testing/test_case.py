from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pytest

from httpx import AsyncClient, ASGITransport

if TYPE_CHECKING:
    from fastapi_startkit import Application


class HttpTestCase(ABC):
    client: AsyncClient

    @pytest.fixture(autouse=True)
    async def setup_client(self):
        async with AsyncClient(
                transport=ASGITransport(app=self.get_application().fastapi), base_url="http://test"
        ) as client:
            self.client = client
            yield

    @abstractmethod
    def get_application(self)->'Application':
        ...

    async def get(self, url, **kwargs):
        return await self.client.get(url, **kwargs)

    async def post(self, url, **kwargs):
        return await self.client.post(url, **kwargs)

    async def put(self, url, **kwargs):
        return await self.client.put(url, **kwargs)

    async def delete(self, url, **kwargs):
        return await self.client.delete(url, **kwargs)
