from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool

from .connection import BaseConnection
from ..query.grammars import SQLiteGrammar
from ..schema.platforms import SQLitePlatform
from ..query.processors import SQLitePostProcessor


class SQLiteConnection(BaseConnection):
    """SQLite implementation of Async SQLAlchemy connection."""

    # Keyed by ":memory:" sentinel; cleared to force a fresh DB on next connect.
    _shared_engines: dict = {}

    def get_connection_url(self):
        database = self.connection_details.get("database")
        return f"sqlite+aiosqlite:///{database}"

    async def make_connection(self):
        """Override to use StaticPool for SQLite (required for :memory: databases)."""
        if not self._engine:
            url = self.get_connection_url()
            engine_kwargs = {"pool_pre_ping": True}
            # :memory: SQLite databases must use a shared StaticPool engine so
            # that all connection instances (Schema, Models, …) see the same DB.
            if ":memory:" in url:
                if url not in SQLiteConnection._shared_engines:
                    engine_kwargs["poolclass"] = StaticPool
                    engine_kwargs["connect_args"] = {"check_same_thread": False}
                    SQLiteConnection._shared_engines[url] = create_async_engine(
                        url, **engine_kwargs
                    )
                self._engine = SQLiteConnection._shared_engines[url]
            else:
                self._engine = create_async_engine(url, **engine_kwargs)

        if self._connection is None:
            self._connection = await self._engine.connect()
            self.open = 1

        return self

    async def close_connection(self):
        """For :memory: databases we still close the AsyncConnection (returns it
        to the StaticPool), but the StaticPool keeps the underlying DBAPI
        connection alive so committed data is visible on the next checkout."""
        await super().close_connection()

    @classmethod
    def get_default_query_grammar(cls):
        return SQLiteGrammar

    @classmethod
    def get_default_platform(cls):
        return SQLitePlatform

    @classmethod
    def get_default_post_processor(cls):
        return SQLitePostProcessor
