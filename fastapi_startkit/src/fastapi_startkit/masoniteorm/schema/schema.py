from fastapi_startkit.masoniteorm.schema.Blueprint import Blueprint
from fastapi_startkit.masoniteorm.schema.Table import Table
from fastapi_startkit.masoniteorm.schema.TableDiff import TableDiff


class Schema:
    def __init__(self, manager) -> None:
        self._manager = manager
        self._connection = None

    def on(self, connection_name: str) -> "Schema":
        """Select which connection to use.  Returns self for chaining."""
        self._connection = self._manager.connection(connection_name)
        return self

    def get_connection(self):
        if self._connection is None:
            self._connection = self._manager.connection(None)

        return self._connection

    def platform(self):
        return self.get_connection().get_default_platform()()

    async def create(self, table: str) -> Blueprint:
        """Return a Blueprint for a new table (async context manager)."""
        connection = self.get_connection()

        return Blueprint(
            grammar=connection.get_query_grammar(),
            connection=connection,
            table=Table(table),
            action="create",
            platform=connection.get_default_platform(),
        )

    async def create_table_if_not_exists(self, table: str) -> Blueprint:
        if self._connection is None:
            self._connection = self._manager.connection(None)

        return Blueprint(
            grammar=self._connection.get_query_grammar(),
            connection=self._connection,
            table=Table(table),
            action="create_table_if_not_exists",
            platform=self._connection.get_default_platform(),
        )

    async def table(self, table: str) -> Blueprint:
        """Return a Blueprint for altering an existing table (async context manager)."""
        if self._connection is None:
            self._connection = self._manager.connection(None)

        return Blueprint(
            grammar=self._connection.get_query_grammar(),
            connection=self._connection,
            table=TableDiff(table),
            action="alter",
            platform=self._connection.get_default_platform(),
        )

    async def drop_table(self, table: str) -> None:
        sql = self.platform().compile_drop_table(table)
        await self.get_connection().statement(sql, ())

    def drop(self, *args, **kwargs):
        return self.drop_table(*args, **kwargs)

    async def drop_table_if_exists(self, table: str) -> None:
        if self._connection is None:
            self._connection = self._manager.connection(None)

        sql = self._connection.get_default_platform()().compile_drop_table_if_exists(table)
        await self._connection.statement(sql, ())

    async def has_table(self, table: str) -> bool:
        if self._connection is None:
            self._connection = self._manager.connection(None)

        sql = self._connection.get_default_platform()().compile_table_exists(table)
        result = await self._connection.run(sql, ())
        return bool(result.fetchall())

    async def rename(self, table: str, new_name: str) -> None:
        if self._connection is None:
            self._connection = self._manager.connection(None)

        sql = self._connection.get_default_platform()().compile_rename_table(table, new_name)
        await self._connection.run(sql, ())

    async def get_all_tables(self):
        """Gets all tables in the database."""
        connection = self.get_connection()
        platform = connection.get_default_platform()()
        sql = platform.compile_get_all_tables(
            database=connection.config.get("database"),
            schema=connection.config.get("schema"),
        )
        result = await connection.select(sql, ())
        return [list(row.values())[0] for row in result] if result else []
