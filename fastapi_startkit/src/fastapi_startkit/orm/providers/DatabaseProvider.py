from fastapi_startkit.masoniteorm.commands import DBSeedCommand
from fastapi_startkit.masoniteorm.commands import MigrateCommand
from fastapi_startkit.orm.connections.factory import ConnectionFactory
from fastapi_startkit.orm.connections.manager import DatabaseManager
from fastapi_startkit.orm.models import Model
from fastapi_startkit.providers.Provider import Provider
from fastapi_startkit.masoniteorm.migrations import Migration


class DatabaseProvider(Provider):
    def register(self):
        db = DatabaseManager(ConnectionFactory(), self.config)

        self.app.bind('db', db)
        self.app.bind('schema', db.get_schema_builder())

        Model.db_manager = db
        Migration.db_manager = db

    def boot(self) -> None:
        self.commands([
            MigrateCommand,
            DBSeedCommand
        ])
