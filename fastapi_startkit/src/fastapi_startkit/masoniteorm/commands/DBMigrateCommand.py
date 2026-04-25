import os
from .Command import Command
from cleo.helpers import option


class DBMigrateCommand(Command):
    name = "db:migrate"
    description = "Run the pending database migrations."

    options = [
        option(
            "migration",
            "m",
            flag=False,
            default="all",
            description="Migration's name to be migrated",
        ),
        option(
            "connection",
            "c",
            flag=False,
            default="default",
            description="The connection you want to run migrations on",
        ),
        option(
            "force",
            "f",
            flag=True,
            description="Force migrations without prompt in production",
        ),
        option(
            "show",
            "s",
            flag=True,
            description="Shows the output of SQL for migrations that would be running",
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

        # prompt user for confirmation in production
        if os.getenv("APP_ENV") == "production" and not self.option("force"):
            answer = ""
            while answer not in ["y", "n"]:
                answer = input(
                    "Do you want to run migrations in PRODUCTION ? (y/n)\n"
                ).lower()
            if answer != "y":
                self.info("Migrations cancelled")
                exit(0)
        migration = Migration(
            command_class=self,
            connection=self.option("connection"),
            migration_directory=self.option("directory"),
        )
        await migration.create_table_if_not_exists()
        if not await migration.get_unran_migrations():
            self.info("Nothing To Migrate!")
            return

        migration_name = self.option("migration")
        show_output = self.option("show")

        await migration.migrate(migration=migration_name, output=show_output)
