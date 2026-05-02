from unittest import IsolatedAsyncioTestCase

from fastapi_startkit.masoniteorm.testing.transaction import RefreshDatabase

from ..fixtures.db import DB
from ..fixtures.migration import migrate, wipe
from ..fixtures.seeder import seeder


class TestCase(RefreshDatabase, IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db = DB
        self.schema = self.db.get_schema_builder()
        await self.migrate_database()

    async def asyncTearDown(self):
        DB.clear()
        await wipe()

    @staticmethod
    async def migrate_database():
        DB.clear()
        await wipe()
        await migrate()
        await seeder()
