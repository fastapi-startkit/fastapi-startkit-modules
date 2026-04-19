from fastapi_startkit.masoniteorm.schema.Blueprint import Blueprint
from fastapi_startkit.masoniteorm.schema.Table import Table
from fastapi_startkit.masoniteorm.schema.TableDiff import TableDiff


class Schema:
    """Schema builder that uses DatabaseManager for connection resolution.

    Usage::

        schema = DB.get_schema_builder()

        async with await schema.on("default").create("users") as table:
            table.id()
            table.string("name")
            table.timestamp("email_verified_at").nullable()
            table.timestamps()
    """

    def __init__(self, manager) -> None:
        self._manager = manager
        self._connection = None

    def on(self, connection_name: str) -> "Schema":
        """Select which connection to use.  Returns self for chaining."""
        self._connection = self._manager.connection(connection_name)
        return self

    async def create(self, table: str) -> Blueprint:
        """Return a Blueprint for a new table (async context manager)."""
        if self._connection is None:
            self._connection = self._manager.connection(None)

        return Blueprint(
            grammar=self._connection.get_query_grammar(),
            connection=self._connection,
            table=Table(table),
            action="create",
            platform=self._connection.get_default_platform(),
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
        if self._connection is None:
            self._connection = self._manager.connection(None)

        sql = self._connection.get_default_platform()().compile_drop_table(table)
        await self._connection.run(sql, ())

    async def drop_table_if_exists(self, table: str) -> None:
        if self._connection is None:
            self._connection = self._manager.connection(None)

        sql = self._connection.get_default_platform()().compile_drop_table_if_exists(table)
        await self._connection.run(sql, ())

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
