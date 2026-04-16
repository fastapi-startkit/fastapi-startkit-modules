from contextlib import asynccontextmanager

from .postgres_connection import PostgresConnection
from .sqlite_connection import SQLiteConnection


class DBManager:
    """Manages async database connections."""
    _drivers = {
        "postgres": PostgresConnection,
        "sqlite": SQLiteConnection,
    }

    _morph_map = {}

    def __init__(self, connection_details=None):
        self.connection_details = connection_details or {}
        self._connections = {}

    def morph_map(self, map):
        self._morph_map = map
        return self

    def get_connection_details(self):
        """Returns the full connection configuration dictionary."""
        return self.connection_details

    def connection(self, name="default", reconnect=False):
        if name == "default":
            name = self.connection_details.get("default", "postgres")

        if name in self._connections and not reconnect:
            return self._connections[name]

        # If reconnect is True, we remove the existing connection from cache
        if reconnect and name in self._connections:
            del self._connections[name]

        config = self.connection_details.get(name)
        if not config:
            raise ValueError(f"Connection {name} not found in configuration.")

        driver = config.get("driver")
        conn_class = self._drivers.get(driver)

        if not conn_class:
            raise ValueError(f"Driver {driver} is not supported.")

        conn = conn_class(
            connection_details=config,
            name=name
        )
        self._connections[name] = conn
        return conn

    async def new_connection(self, name="default"):
        """Acquire a new connection asynchronously."""
        conn = self.connection(name)
        return await conn.make_connection()

    async def begin_transaction(self, name="default"):
        """Start a new transaction."""
        return await self.connection(name).begin()

    async def commit_transaction(self, name="default"):
        """Commit the current transaction."""
        return await self.connection(name).commit()

    async def rollback_transaction(self, name="default"):
        """Rollback the current transaction."""
        return await self.connection(name).rollback()

    @asynccontextmanager
    async def transaction(self, name="default"):
        """Async context manager for transactions."""
        conn = self.connection(name)
        await conn.begin()
        try:
            yield conn
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise
