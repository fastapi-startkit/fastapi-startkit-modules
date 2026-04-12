from .Command import Command


class MigrateResetCommand(Command):
    """
    Reset migrations.

    migrate:reset
        {--m|migration=all : Migration's name to be rollback}
        {--c|connection=default : The connection you want to run migrations on}
        {--schema=? : Sets the schema to be migrated}
        {--d|directory=databases/migrations : The location of the migration directory}
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

        await migration.reset(self.option("migration"))
