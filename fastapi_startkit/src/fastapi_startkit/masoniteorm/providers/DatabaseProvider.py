from ...providers.Provider import Provider
from ..commands import (
    MakeMigrationCommand,
    MakeModelCommand,
    MakeObserverCommand,
    MakeSeedCommand,
    DBMigrateCommand,
    MigrateFreshCommand,
    MigrateRefreshCommand,
    MigrateResetCommand,
    MigrateRollbackCommand,
    MigrateStatusCommand,
    MakeModelDocstringCommand,
    DBSeedCommand,
)


class DatabaseProvider(Provider):
    """Database provider for Masonite ORM."""

    def register(self):
        self.commands([
            MakeMigrationCommand(),
            MakeSeedCommand(),
            MakeObserverCommand(),
            DBMigrateCommand(),
            MigrateResetCommand(),
            MakeModelCommand(),
            MigrateStatusCommand(),
            MigrateRefreshCommand(),
            MigrateFreshCommand(),
            MigrateRollbackCommand(),
            DBSeedCommand(),
            MakeModelDocstringCommand(),
        ])

    def boot(self):
        pass
