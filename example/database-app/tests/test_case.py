import gc
import pytest
from httpx import AsyncClient, ASGITransport
from bootstrap.application import app

class TestCase:
    @pytest.fixture(autouse=True)
    async def setup_client(self):
        async with AsyncClient(
            transport=ASGITransport(app=app.fastapi), base_url="http://test"
        ) as client:
            self.client = client
            yield

    async def get(self, url, **kwargs):
        return await self.client.get(url, **kwargs)

    async def post(self, url, **kwargs):
        return await self.client.post(url, **kwargs)

    async def put(self, url, **kwargs):
        return await self.client.put(url, **kwargs)

    async def delete(self, url, **kwargs):
        return await self.client.delete(url, **kwargs)


class RefreshDatabase:
    migrated = False

    @staticmethod
    async def migrate_database():
        from fastapi_startkit.masoniteorm.migrations import Migration

        if not RefreshDatabase.migrated:
            migration = Migration(migration_directory="databases/migrations")
            await migration.fresh(ignore_fk=True)
            RefreshDatabase.migrated = True

    @pytest.fixture(autouse=True)
    async def refresh_database(self):
        await RefreshDatabase.migrate_database()

        from fastapi_startkit.masoniteorm.models import Model
        db_connection = Model.db_manager.connection(None)
        original_engine = db_connection.conn

        async with original_engine.connect() as conn:
            transaction = await conn.begin()

            original_commit = conn.sync_connection.commit
            conn.sync_connection.commit = lambda: None

            class PatchedEngine:
                def connect(self):
                    return YieldConn()

            class YieldConn:
                async def __aenter__(self):
                    return conn

                async def __aexit__(self, *args):
                    pass

            db_connection.conn = PatchedEngine()

            yield

            db_connection.conn = original_engine
            conn.sync_connection.commit = original_commit
            await transaction.rollback()

        await original_engine.dispose()
        gc.collect()