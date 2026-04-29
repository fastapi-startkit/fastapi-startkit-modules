from cleo.helpers import option
from .Command import Command


class MigrateFreshCommand(Command):
    name = "db:migrate:fresh"
    description = "Fresh migrations."

    options = [
        option(
            "connection",
            "c",
            flag=False,
            default="default",
            description="The connection you want to run migrations on",
        ),
        option(
            "directory",
            "d",
            flag=False,
            default="databases/migrations",
            description="The location of the migration directory",
        ),
        option(
            "no-fk", None, flag=True, description="Re-enable foreign key constraints during drop"
        ),
        option(
            "seed",
            "s",
            flag=False,
            default=None,
            description="Seed the database after fresh",
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
        )

        await migration.fresh(ignore_fk=not self.option("no-fk"))

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
