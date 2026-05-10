from unittest import IsolatedAsyncioTestCase

from fastapi_startkit.masoniteorm.testing.transaction import RefreshDatabase

from .fixtures.db import DB
from ..fixtures.migration import migrate, wipe
from ..fixtures.seeder import seeder


class TestCase(RefreshDatabase, IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db = DB
        self.schema = DB.get_schema_builder()
        await self.migrate_database()

    async def asyncTearDown(self):
        await DB.clear()
        await wipe(DB.get_schema_builder())

    @staticmethod
    async def migrate_database():
        await DB.clear()
        schema = DB.get_schema_builder()
        await wipe(schema)
        await migrate(schema)
        await seeder()
