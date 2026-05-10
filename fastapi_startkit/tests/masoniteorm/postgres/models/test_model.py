from unittest import IsolatedAsyncioTestCase

from fastapi_startkit.masoniteorm.models.model import Model
from fastapi_startkit.masoniteorm.testing.transaction import RefreshDatabase
from ..fixtures.db import DB, schema
from ...fixtures.migration import migrate, wipe
from ...fixtures.model import User


class TestPostGresModel(RefreshDatabase, IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        Model.db_manager = DB
        await DB.clear()
        await wipe(schema)
        await migrate(schema)

    async def asyncTearDown(self):
        await wipe(schema)
        await DB.clear()

    async def test_can_create_and_find_user(self):
        user = await User.create({"name": "Alice", "email": "alice@example.com", "is_admin": False})
        self.assertIsNotNone(user.id)

        found = await User.find(user.id)
        self.assertEqual(found.name, "Alice")
        self.assertEqual(found.email, "alice@example.com")
