from unittest import IsolatedAsyncioTestCase

from fastapi_startkit.masoniteorm.migrations.Migration import Migration
from fastapi_startkit.masoniteorm.models.MigrationModel import MigrationModel

from tests.masoniteorm.sqlite.fixtures.db import DB


class TestMigration(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        Migration.db_manager = DB
        MigrationModel.db_manager = DB
        self.migration = Migration(connection="sqlite")
        self.schema = DB.get_schema_builder()
        await self.migration.fresh()

    async def asyncTearDown(self):
        await DB.clear()

    async def test_fresh_creates_migrations_table(self):
        tables = await self.schema.get_all_tables()
        self.assertIn("migrations", tables)

    async def test_fresh_runs_all_migrations(self):
        tables = await self.schema.get_all_tables()
        self.assertIn("posts", tables)

    async def test_migrations_table_primary_key_is_id(self):
        record = await MigrationModel.create(
            {"migration": "2026_01_01_000000_create_posts_table", "batch": 1}
        )

        self.assertIsNotNone(record.id)
        self.assertIsInstance(record.id, int)

    async def test_migration_record_is_fetchable_by_id(self):
        record = await MigrationModel.where(
            "migration", "2026_01_01_000000_create_posts_table"
        ).first()

        self.assertIsNotNone(record)
        self.assertEqual(record.batch, 1)
        self.assertIsNotNone(record.id)
