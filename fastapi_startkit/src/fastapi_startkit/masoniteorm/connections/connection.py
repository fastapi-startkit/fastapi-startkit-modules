from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from ..exceptions import QueryException


class BaseConnection:
    def __init__(self, connection_details=None, name=None):
        self.connection_details = connection_details or {}
        self.name = name or "default"

        # Ensure these are localized to the instance to avoid class-level sharing
        self._engine = None
        self._connection = None
        self._transaction = None

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
        """Initializes the async engine and acquires a connection from the pool."""
        if not self._engine:
            # Initialize engine with pooling options
            options = self.connection_details.get("options", {})
            min_size = options.get("min_size", 1)
            max_size = options.get("max_size", 10)

            self._engine = create_async_engine(
                self.get_connection_url(),
                pool_size=max_size,
                max_overflow=0,
                pool_pre_ping=True,
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

            result = await self._connection.execute(statement, bindings if not "?" in query else None)

            if self.get_transaction_level() <= 0:
                await self._connection.commit()

            if results == 1:
                row = result.fetchone()
                return dict(row._mapping) if row else {}
            else:
                try:
                    row_results = result.fetchall()
                    return [dict(row._mapping) for row in row_results]
                except Exception:
                    return {}

        except Exception as e:
            raise QueryException(str(e)) from e
        finally:
            if self.get_transaction_level() <= 0:
                await self.close_connection()
