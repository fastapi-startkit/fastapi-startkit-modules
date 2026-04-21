from unittest import IsolatedAsyncioTestCase
from .Database import Database

class TestCase(IsolatedAsyncioTestCase, Database):
    async def asyncSetUp(self):
        await self.setUpDatabase()
        await self.beginTransaction()

    async def asyncTearDown(self):
        await self.rollbackTransaction()
