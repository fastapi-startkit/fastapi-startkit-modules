import os
from ..config import load_config
from ..migrations import Migration
from ..seeds import Seeder

class Database:
    _migrated = False
    migration_directory = "databases/migrations"
    seed_path = "databases/seeds"

    async def setUpDatabase(self):
        """
        Run migrations once per test suite.
        """
        if not Database._migrated:
            migration = Migration(
                migration_directory=self.migration_directory
            )
            await migration.create_table_if_not_exists()
            await migration.migrate()
            Database._migrated = True

    async def beginTransaction(self):
        """
        Start a transaction for the current test and make it sticky in the resolver.
        """
        resolver = load_config().DB
        # We handle the session and transaction manually to ensure we can FORCE a rollback
        self._session = resolver.get_session_factory()()
        await self._session.__aenter__()
        self._transaction = await self._session.begin()
        
        # Make this session "sticky" so QueryBuilder uses it
        resolver.set_sticky_session(self._session)

    async def rollbackTransaction(self):
        """
        Rollback the transaction after the test and clear the sticky session.
        """
        resolver = load_config().DB
        resolver.remove_sticky_session()
        
        if hasattr(self, "_transaction"):
            await self._transaction.rollback()
        
        if hasattr(self, "_session"):
            await self._session.__aexit__(None, None, None)

    async def seed(self, *seeder_classes):
        """
        Run seeders.
        """
        seeder = Seeder(seed_path=self.seed_path)
        if seeder_classes:
            await seeder.call(*seeder_classes)
        else:
            await seeder.run_database_seed()
