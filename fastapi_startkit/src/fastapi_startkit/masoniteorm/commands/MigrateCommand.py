import os
from .Command import Command


class MigrateCommand(Command):
    """
    Run migrations.

    migrate
        {--m|migration=all : Migration's name to be migrated}
        {--c|connection=default : The connection you want to run migrations on}
        {--f|force : Force migrations without prompt in production}
        {--s|show : Shows the output of SQL for migrations that would be running}
        {--schema=? : Sets the schema to be migrated}
        {--d|directory=databases/migrations : The location of the migration directory}
    """

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
            config_path=self.option("config"),
            schema=self.option("schema"),
        )
        await migration.create_table_if_not_exists()
        if not await migration.get_unran_migrations():
            self.info("Nothing To Migrate!")
            return

        migration_name = self.option("migration")
        show_output = self.option("show")

        await migration.migrate(migration=migration_name, output=show_output)
