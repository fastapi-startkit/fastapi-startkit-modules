from pathlib import Path

from fastapi_startkit.masoniteorm.commands import (
    DBSeedCommand,
    MakeMigrationCommand,
    MakeModelCommand,
    MakeSeedCommand,
    DBMigrateCommand,
    MigrateStatusCommand,
    MigrateRollbackCommand,
    MigrateFreshCommand
)
from fastapi_startkit.masoniteorm.connections.factory import ConnectionFactory
from fastapi_startkit.masoniteorm.connections.manager import DatabaseManager
from fastapi_startkit.masoniteorm.migrations import Migration
from fastapi_startkit.masoniteorm.models import Model
from fastapi_startkit.providers.Provider import Provider


class DatabaseProvider(Provider):
    def register(self):
        from ..config.database import DatabaseConfig
        config =self.resolve_config(DatabaseConfig)
        self.merge_config_from(config, self.provider_key)

        db = DatabaseManager(ConnectionFactory(), config)

        self.app.bind('db', db)
        self.app.bind('schema', db.get_schema_builder())

        Model.db_manager = db
        Migration.db_manager = db

    def boot(self) -> None:
        self.publishes({
            Path(__file__).resolve().parent.parent.joinpath('config/database.py'): 'config/database.py'
        })

        self.commands([
            DBMigrateCommand,
            DBSeedCommand,
            MakeMigrationCommand,
            MigrateStatusCommand,
            MigrateRollbackCommand,
            MakeModelCommand,
            MakeSeedCommand,
            MigrateFreshCommand
        ])
