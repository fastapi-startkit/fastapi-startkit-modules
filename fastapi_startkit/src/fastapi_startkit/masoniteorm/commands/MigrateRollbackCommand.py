from cleo.helpers import option
from .Command import Command


class MigrateRollbackCommand(Command):
    name = "migrate:rollback"
    description = "Rolls back the last batch of migrations."

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
            "show",
            "s",
            flag=True,
            description="Shows the output of SQL for migrations that would be running",
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
    ]

    def handle(self):
        import asyncio
        return asyncio.run(self.handle_async())

    async def handle_async(self):
        from ..migrations import Migration
        await Migration(
            command_class=self,
            connection=self.option("connection"),
            migration_directory=self.option("directory"),
            config_path=self.option("config"),
            schema=self.option("schema"),
        ).rollback(
            migration=self.option("migration"), output=self.option("show")
        )
