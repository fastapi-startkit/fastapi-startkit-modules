import gc
import pytest

async def _wrap_in_transaction():
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


class DatabaseTransaction:
    @pytest.fixture(autouse=True)
    async def database_transaction(self):
        async for _ in _wrap_in_transaction():
            yield


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
        get_app = getattr(self, 'get_application', None)
        if get_app:
            get_app()
        await RefreshDatabase.migrate_database()
        async for _ in _wrap_in_transaction():
            yield
