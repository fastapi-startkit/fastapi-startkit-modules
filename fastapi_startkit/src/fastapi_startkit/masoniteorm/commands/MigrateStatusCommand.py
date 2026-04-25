from cleo.helpers import option
from ..migrations import Migration
from .Command import Command


class MigrateStatusCommand(Command):
    name = "db:migrate:status"
    description = "Display migrations status."

    options = [
        option(
            "connection",
            "c",
            flag=False,
            default="default",
            description="The connection you want to run migrations on",
        ),
        option(
            "schema",
            None,
            flag=False,
            default=None,
            description="Sets the schema to be migrated",
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
        migration = Migration(
            command_class=self,
            connection=self.option("connection"),
            migration_directory=self.option("directory"),
            config_path=self.option("config"),
            schema=self.option("schema"),
        )
        await migration.create_table_if_not_exists()
        table = self.table()
        table.set_header_row(["Ran?", "Migration", "Batch"])
        migrations = []

        ran_migrations = await migration.get_ran_migrations()
        for migration_data in ran_migrations:
            migration_file = migration_data["migration_file"]
            batch = migration_data["batch"]

            migrations.append(
                [
                    "<info>Y</info>",
                    f"<comment>{migration_file}</comment>",
                    f"<info>{batch}</info>",
                ]
            )

        unran_migrations = await migration.get_unran_migrations()
        for migration_file in unran_migrations:
            migrations.append(
                [
                    "<error>N</error>",
                    f"<comment>{migration_file}</comment>",
                    "<info>-</info>",
                ]
            )

        table.set_rows(migrations)

        table.render(self.io)
