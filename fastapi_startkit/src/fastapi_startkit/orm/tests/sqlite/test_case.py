from unittest import IsolatedAsyncioTestCase

from ..fixtures.db import DB
from ..fixtures.migration import migrate


class TestCase(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db = DB
        self.schema = self.db.get_schema_builder()
        await self.rollback()
        await migrate()

    async def asyncTearDown(self):
        await self.rollback()

    async def rollback(self):
        await self.schema.drop_table_if_exists("users")
