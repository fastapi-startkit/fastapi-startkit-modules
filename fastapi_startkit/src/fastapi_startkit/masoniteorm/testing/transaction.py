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
            from fastapi_startkit.masoniteorm.migrations import Migration

            await Migration(migration_directory="databases/migrations").fresh(ignore_fk=True)
            RefreshDatabase.migrated = True
