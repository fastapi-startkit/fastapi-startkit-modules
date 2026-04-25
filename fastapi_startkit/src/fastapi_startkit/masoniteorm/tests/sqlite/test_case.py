from unittest import IsolatedAsyncioTestCase

from ..fixtures.db import DB
from ..fixtures.migration import migrate, wipe
from ..fixtures.seeder import seeder


class TestCase(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db = DB
        self.schema = self.db.get_schema_builder()
        await self.rollback()
        await migrate()
        await seeder()

    async def asyncTearDown(self):
        await self.rollback()

    async def rollback(self) -> None:
        await wipe()
