from .Command import Command


class MigrateRefreshCommand(Command):
    """
    Refresh migrations.

    migrate:refresh
        {--m|migration=all : Migration's name to be rollback}
        {--c|connection=default : The connection you want to run migrations on}
        {--schema=? : Sets the schema to be migrated}
        {--d|directory=databases/migrations : The location of the migration directory}
        {--s|seed=? : Seed the database after refresh}
        {--seed-directory=databases/seeds : The location of the seed directory}
    """

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
