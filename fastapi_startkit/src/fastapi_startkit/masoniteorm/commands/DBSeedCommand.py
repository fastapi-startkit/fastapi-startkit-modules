from cleo.helpers import argument, option
from inflection import camelize, underscore
from .Command import Command


class DBSeedCommand(Command):
    name = "db:seed"
    description = "Run seeds."

    arguments = [
        argument("table", default="None", description="Name of the table to seed", optional=True)
    ]

    options = [
        option(
            "connection",
            "c",
            flag=False,
            default="default",
            description="The connection you want to run migrations on",
        ),
        option("dry", None, description="If the seed should run in dry mode", flag=True),
        option(
            "directory",
            "d",
            flag=False,
            default="databases/seeds",
            description="The location of the seed directory",
        ),
    ]

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
