from cleo.helpers import option
from .Command import Command


class MigrateRefreshCommand(Command):
    name = "migrate:refresh"
    description = "Refresh migrations."

    options = [
        option(
            "migration",
            "m",
            flag=False,
            default="all",
            description="Migration's name to be rollback",
        ),
        option(
            "connection",
            "c",
            flag=False,
            default="default",
            description="The connection you want to run migrations on",
        ),
        option(
            "schema", None, flag=False, default=None, description="Sets the schema to be migrated"
        ),
        option(
            "directory",
            "d",
            flag=False,
            default="databases/migrations",
            description="The location of the migration directory",
        ),
        option(
            "seed",
            "s",
            flag=False,
            default=None,
            description="Seed the database after refresh",
        ),
        option(
            "seed-directory",
            None,
            flag=False,
            default="databases/seeds",
            description="The location of the seed directory",
        ),
    ]

    def handle(self):
        import asyncio
        return asyncio.run(self.handle_async())

    async def handle_async(self):
        from ..migrations import Migration
        migration = Migration(
            command_class=self,
            connection=self.option("connection"),
            migration_directory=self.option("directory"),
            config_path=self.option("config"),
            schema=self.option("schema"),
        )

        await migration.refresh(self.option("migration"))

        if self.option("seed") == "null":
            self.call(
                "seed:run",
                f"None --directory {self.option('seed-directory')} --connection {self.option('connection')}",
            )
        elif self.option("seed"):
            self.call(
                "seed:run",
                f"{self.option('seed')} --directory {self.option('seed-directory')} --connection {self.option('connection')}",
            )
