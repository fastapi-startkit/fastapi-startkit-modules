from typing import Any

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from sqlalchemy.exc import ResourceClosedError
from sqlalchemy.pool import NullPool

from ..exceptions import QueryException


class BaseConnection:
    def __init__(self, connection_details=None, name=None):
        self.connection_details = connection_details or {}
        self.name = name or "default"

        # Ensure these are localized to the instance to avoid class-level sharing
        self._engine = None
        self._connection = None
        self._transaction = None
        self._row_count = 0
        self._last_row_id = None

        self.transaction_level = 0
        self.open = 0
        self.schema = self.connection_details.get("schema")

    def get_connection_url(self):
        """Should be implemented by the driver subclass."""
        raise NotImplementedError("Drivers must implement get_connection_url()")

    def set_schema(self, schema):
        self.schema = schema
        return self

    async def make_connection(self):
        """Initializes the async engine and acquires a connection."""
        if not self._engine:
            # NullPool: BaseConnection is a long-lived singleton (cached in ConnectionFactory).
            # A single physical connection is opened once and reused for all queries.
            # No connection pooling is needed; NullPool avoids GC warnings from idle
            # pool connections being collected without being returned.
            self._engine = create_async_engine(
                self.get_connection_url(),
                poolclass=NullPool,
            )

        if self._connection is None:
            self._connection = await self._engine.connect()
            self.open = 1

        return self

    async def new_connection(self):
        """Alias for make_connection to support fluent async syntax."""
        return await self.make_connection()

    def get_database_name(self):
        return self.connection_details.get("database")

    async def reconnect(self):
        await self.close_connection()
        await self.make_connection()

    async def close_connection(self):
        if self._connection:
            if self._transaction:
                await self._transaction.rollback()
                self._transaction = None
            await self._connection.close()
            self._connection = None
        if self._engine:
            await self._engine.dispose()
            self._engine = None
        self.open = 0

    async def begin(self):
        if not self._connection:
            await self.make_connection()

        if self.transaction_level == 0:
            self._transaction = await self._connection.begin()

        self.transaction_level += 1
        return self

    async def commit(self):
        if self.transaction_level == 1 and self._transaction:
            await self._transaction.commit()
            self._transaction = None

        self.transaction_level = max(0, self.transaction_level - 1)

    async def rollback(self):
        if self.transaction_level == 1 and self._transaction:
            await self._transaction.rollback()
            self._transaction = None

        self.transaction_level = max(0, self.transaction_level - 1)

    def get_transaction_level(self):
        return self.transaction_level

    def get_row_count(self):
        return self._row_count

    def get_last_row_id(self):
        return self._last_row_id

    async def run(self, query: str, bindings = ()):
        if not self._connection:
            await self.reconnect()

        assert self._connection is not None
        statement = self.bind_qmark(query, bindings or ())
        return await self._connection.execute(statement)

    @classmethod
    def bind_qmark(cls, query: str, bindings= ()):
        if "?" in query:
            new_query = query
            new_bindings = {}
            for i, val in enumerate(bindings):
                placeholder = f"p{i}"
                new_query = new_query.replace("?", f":{placeholder}", 1)
                new_bindings[placeholder] = val
            return text(new_query).bindparams(**new_bindings)

        return text(query)

    async def select_one(self, query: str, bindings= ()) -> dict | None:
        result = await self.run(query, bindings)
        row = result.fetchone()
        return dict(zip(result.keys(), row)) if row else None

    async def query(self, query, bindings=(), results="*"):
        """Execute async query using SQLAlchemy text() wrapper."""
        try:
            if not self._connection:
                await self.make_connection()

            # Handle Masonite-style '?' placeholders
            if "?" in query:
                new_query = query
                new_bindings = {}
                for i, val in enumerate(bindings):
                    placeholder = f"p{i}"
                    new_query = new_query.replace("?", f":{placeholder}", 1)
                    new_bindings[placeholder] = val
                statement = text(new_query).bindparams(**new_bindings)
            else:
                statement = text(query)
                new_query = query

            result = await self._connection.execute(statement, bindings if "?" not in query else None)
            self._row_count = result.rowcount
            self._last_row_id = getattr(result, "lastrowid", None)

            if results == 1:
                try:
                    row = result.fetchone()
                    fetched = dict(row._mapping) if row else {}
                except ResourceClosedError:
                    # asyncpg executes text() DML via execute() which discards RETURNING rows.
                    # Fall back to SELECT lastval() to recover the inserted primary key.
                    if "RETURNING" in query.upper():
                        try:
                            lastval_result = await self._connection.execute(text("SELECT lastval() AS lastval"))
                            lastval_row = lastval_result.fetchone()
                            fetched = {"lastval": lastval_row[0]} if lastval_row else {}
                        except Exception:
                            fetched = {}
                    else:
                        fetched = {}
            else:
                try:
                    row_results = result.fetchall()
                    fetched = [dict(row._mapping) for row in row_results]
                except ResourceClosedError:
                    fetched = []

            if self.get_transaction_level() <= 0:
                await self._connection.commit()

            return fetched

        except Exception as e:
            # Roll back the failed statement so the connection is reusable.
            if self._connection and self.get_transaction_level() <= 0:
                try:
                    await self._connection.rollback()
                except Exception:
                    pass
            raise QueryException(str(e)) from e
