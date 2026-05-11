from unittest import IsolatedAsyncioTestCase

from fastapi_startkit.masoniteorm import Model
from fastapi_startkit.masoniteorm.testing.transaction import RefreshDatabase
from .fixtures.db import DB, schema
from ..fixtures.migration import migrate, wipe


class TestCase(RefreshDatabase, IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        Model.db_manager = DB
        await DB.clear()
        await wipe(schema)
        await migrate(schema)

    async def asyncTearDown(self):
        await wipe(schema)
        await DB.clear()
