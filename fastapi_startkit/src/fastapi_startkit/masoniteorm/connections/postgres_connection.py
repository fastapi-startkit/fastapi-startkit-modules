from sqlalchemy import text
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
        """Execute an INSERT ... RETURNING * and return the generated primary key."""
        query_str, params = self.sql_alchemy_bindings(query, bindings)
        conn = await self.get_connection()
        result = await conn.execute(text(query_str), params or {})

        if not self.transactions:
            await conn.commit()

        row = result.fetchone()
        if row:
            return row[0]

        # Fallback for cases where RETURNING result is unavailable
        val_result = await conn.execute(text("SELECT lastval()"))
        val_row = val_result.fetchone()
        return val_row[0] if val_row else None
