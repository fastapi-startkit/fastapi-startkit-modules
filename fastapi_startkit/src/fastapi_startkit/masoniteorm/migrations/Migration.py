import os
from os import listdir
from os.path import isfile, join
from pydoc import locate
from timeit import default_timer as timer

from inflection import camelize

from ..models.MigrationModel import MigrationModel


class Migration:
    db_manager: "DatabaseManager"

    def __init__(
        self,
        connection="default",
        command_class=None,
        migration_directory="databases/migrations",
    ):
        self.connection = connection
        self.migration_directory = migration_directory
        self.last_migrations_ran = []
        self.command_class = command_class

        self.schema = self.db_manager.get_schema_builder()

        self.migration_model = MigrationModel.on(self.connection)

    async def create_table_if_not_exists(self):
        async with await self.schema.create_table_if_not_exists("migrations") as table:
            table.increments("migration_id")
            table.string("migration")
            table.integer("batch")

    async def get_unran_migrations(self):
        directory_path = os.path.join(os.getcwd(), self.migration_directory)
        all_migrations = [
            f.replace(".py", "")
            for f in listdir(directory_path)
            if isfile(join(directory_path, f)) and f != "__init__.py" and not f.startswith(".")
        ]
        all_migrations.sort()
        unran_migrations = []
        database_migrations = await self.migration_model.get()
        for migration in all_migrations:
            if migration not in database_migrations.pluck("migration"):
                unran_migrations.append(migration)
        return unran_migrations

    async def get_rollback_migrations(self):
        all_migrations = await self.migration_model.all()
        return (
            await self.migration_model.where("batch", all_migrations.max("batch"))
            .order_by("migration_id", "desc")
            .get()
        ).pluck("migration")

    async def get_all_migrations(self, reverse=False):
        if reverse:
            return (await self.migration_model.order_by("migration_id", "desc").get()).pluck("migration")

        return (await self.migration_model.all()).pluck("migration")

    async def get_last_batch_number(self):
        return (await self.migration_model.all()).max("batch") or 0

    async def delete_migration(self, file_path):
        return await self.migration_model.where("migration", file_path).delete()

    def locate(self, file_name):
        migration_name = camelize("_".join(file_name.split("_")[4:]).replace(".py", ""))
        file_name = file_name.replace(".py", "")
        migration_directory = self.migration_directory.replace("/", ".").replace("\\", ".")
        return locate(f"{migration_directory}.{file_name}.{migration_name}")

    async def get_ran_migrations(self):
        directory_path = os.path.join(os.getcwd(), self.migration_directory)
        all_migrations = [
            f.replace(".py", "")
            for f in listdir(directory_path)
            if isfile(join(directory_path, f)) and f != "__init__.py" and not f.startswith(".")
        ]
        all_migrations.sort()
        ran = []

        database_migrations = await self.migration_model.all()
        for migration in all_migrations:
            matched_migration = database_migrations.where("migration", migration).first()
            if matched_migration:
                ran.append(
                    {
                        "migration_file": matched_migration.migration,
                        "batch": matched_migration.batch,
                    }
                )
        return ran

    async def migrate(self, migration="all", output=False):
        default_migrations = await self.get_unran_migrations()
        migrations = default_migrations if migration == "all" else [migration]

        batch = int(await self.get_last_batch_number() or 0) + 1

        for migration in migrations:
            try:
                migration_class = self.locate(migration)
            except TypeError:
                migration_class = None

            if migration_class is None:
                if self.command_class:
                    self.command_class.line(f"<error>Not Found: {migration}</error>")
                continue

            self.last_migrations_ran.append(migration)
            if self.command_class:
                self.command_class.line(f"<comment>Migrating:</comment> <question>{migration}</question>")

            migration_class = migration_class(connection=self.connection)

            if output:
                migration_class.schema.dry()
            start = timer()
            await migration_class.up()
            duration = "{:.2f}".format(timer() - start)

            if output:
                if self.command_class:
                    table = self.command_class.table()
                    table.set_header_row(["SQL"])
                    sql = migration_class.schema._blueprint.to_sql()
                    if isinstance(sql, list):
                        sql = ",".join(sql)
                    table.set_rows([[sql]])
                    table.render(self.command_class.io)
                    continue
                else:
                    print(migration_class.schema._blueprint.to_sql())

            if self.command_class:
                self.command_class.line(f"<info>Migrated:</info> <question>{migration}</question> ({duration}s)")

            await self.migration_model.create({"batch": batch, "migration": migration.replace(".py", "")})

    async def rollback(self, migration="all", output=False):
        default_migrations = await self.get_rollback_migrations()
        migrations = default_migrations if migration == "all" else [migration]

        for migration in migrations:
            if migration.endswith(".py"):
                migration = migration.replace(".py", "")

            if self.command_class:
                self.command_class.line(f"<comment>Rolling back:</comment> <question>{migration}</question>")

            try:
                migration_class = self.locate(migration)
            except TypeError:
                self.command_class.line(f"<error>Not Found: {migration}</error>")
                continue

            migration_class = migration_class(connection=self.connection, schema=self.schema_name)

            if output:
                migration_class.schema.dry()

            start = timer()
            await migration_class.down()
            duration = "{:.2f}".format(timer() - start)

            if output:
                if self.command_class:
                    table = self.command_class.table()
                    table.set_header_row(["SQL"])
                    if hasattr(migration_class.schema, "_blueprint") and migration_class.schema._blueprint:
                        sql = migration_class.schema._blueprint.to_sql()
                        if isinstance(sql, list):
                            sql = ",".join(sql)

                        table.set_rows([[sql]])
                    elif migration_class.schema._sql:
                        table.set_rows([[migration_class.schema._sql]])
                    table.render(self.command_class.io)
                    continue
                else:
                    print(migration_class.schema._blueprint.to_sql())

            await self.delete_migration(migration)

            if self.command_class:
                self.command_class.line(f"<info>Rolled back:</info> <question>{migration}</question> ({duration}s)")

    async def delete_migrations(self, migrations=None):
        return await self.migration_model.where_in("migration", migrations or []).delete()

    async def delete_last_batch(self):
        return await self.migration_model.where("batch", await self.get_last_batch_number()).delete()

    async def reset(self, migration="all"):
        default_migrations = await self.get_all_migrations(reverse=True)
        migrations = default_migrations if migration == "all" else [migration]

        if not len(migrations):
            if self.command_class:
                self.command_class.line("<info>Nothing to reset</info>")
            else:
                print("Nothing to reset")

        for migration in migrations:
            if self.command_class:
                self.command_class.line(f"<comment>Rolling back:</comment> <question>{migration}</question>")

            try:
                migration_instance = self.locate(migration)(connection=self.connection, schema=self.schema_name)
                await migration_instance.down()
            except TypeError:
                self.command_class.line(f"<error>Not Found: {migration}</error>")
                continue

                # raise MigrationNotFound(f"Could not find {migration}")

            await self.delete_migration(migration)

            if self.command_class:
                self.command_class.line(f"<info>Rolled back:</info> <question>{migration}</question>")

            await self.delete_migrations([migration])

        if self.command_class:
            self.command_class.line("")

    async def refresh(self, migration="all"):
        await self.reset(migration)
        await self.migrate(migration)

    async def drop_all_tables(self, ignore_fk=False):
        if self.command_class:
            self.command_class.line("<comment>Dropping all tables</comment>")

        if ignore_fk:
            await self.schema.disable_foreign_key_constraints()

        for table in await self.schema.get_all_tables():
            await self.schema.drop(table)

        if ignore_fk:
            await self.schema.enable_foreign_key_constraints()

        if self.command_class:
            self.command_class.line("<info>All tables dropped</info>")

    async def fresh(self, ignore_fk=False, migration="all"):
        await self.drop_all_tables(ignore_fk=ignore_fk)
        await self.create_table_if_not_exists()

        if not await self.get_unran_migrations():
            if self.command_class:
                self.command_class.line("<comment>Nothing to migrate</comment>")
            return

        await self.migrate(migration)
