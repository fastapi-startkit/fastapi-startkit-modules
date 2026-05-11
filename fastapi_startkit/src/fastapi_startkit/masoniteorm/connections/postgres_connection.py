from fastapi_startkit.masoniteorm.query.grammars import PostgresGrammar
from fastapi_startkit.masoniteorm.query.processors import PostgresPostProcessor
from fastapi_startkit.masoniteorm.schema.platforms import PostgresPlatform
from .connection import Connection


class PostgresConnection(Connection):
    """Async PostgreSQL connection backed by asyncpg via SQLAlchemy."""

    @classmethod
    def get_query_grammar(cls):
        return PostgresGrammar

    @classmethod
    def get_default_platform(cls):
        return PostgresPlatform

    @classmethod
    def get_post_processor(cls):
        return PostgresPostProcessor

    async def insert(self, query: str, bindings: list | None = None) -> int | None:
        """Execute INSERT ... RETURNING "pk" and return the generated primary key.

        The base Connection.insert() uses lastrowid which is SQLite-specific.
        PostgreSQL uses RETURNING to get the pk back; the grammar scopes it to
        the exact primary key column so row[0] is always the pk value.
        """
        result = await self.execute(query, bindings)
        row = result.fetchone()
        return row[0] if row else None
