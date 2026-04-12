from inflection import camelize, underscore

from .Command import Command


class DBSeedCommand(Command):
    """
    Run seeds.

    db:seed
        {--c|connection=default : The connection you want to run migrations on}
        {--dry : If the seed should run in dry mode}
        {table=None : Name of the table to seed}
        {--d|directory=databases/seeds : The location of the seed directory}
    """

    def handle(self):
        import asyncio
        return asyncio.run(self.handle_async())

    async def handle_async(self):
        from ..seeds import Seeder
        seeder = Seeder(
            dry=self.option("dry"),
            seed_path=self.option("directory"),
            connection=self.option("connection"),
        )

        if self.argument("table") == "None":
            await seeder.run_database_seed()
            seeder_seeded = "Database Seeder"

        else:
            table = self.argument("table")
            seeder_file = f"{underscore(table)}_table_seeder.{camelize(table)}TableSeeder"
            await seeder.run_specific_seed(seeder_file)
            seeder_seeded = f"{camelize(table)}TableSeeder"

        self.line(f"<info>{seeder_seeded} seeded!</info>")
