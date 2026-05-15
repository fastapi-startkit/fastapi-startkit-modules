class DatabaseTransaction:
    async def asyncStartTestRun(self):
        from fastapi_startkit.masoniteorm.models import Model

        self.connection = Model.db_manager.connection(None)
        await self.connection.begin_transaction()

    async def asyncStopTestRun(self):
        await self.connection.rollback()


class RefreshDatabase(DatabaseTransaction):
    migrated = False

    async def asyncStartTestRun(self):
        await self.migrate_database()
        await super().asyncStartTestRun()

    @staticmethod
    async def migrate_database():
        if not RefreshDatabase.migrated:
            from fastapi_startkit.masoniteorm.migrations import Migrator
            from fastapi_startkit.application import app as get_app

            migration_dir = get_app().use_base_path("databases/migrations")
            migrator = Migrator(migration_directory=migration_dir)
            await migrator.fresh(ignore_fk=True)
            RefreshDatabase.migrated = True
