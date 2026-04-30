from typing import Any
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

    async def insert(self, query: str, bindings: list | None = None) -> Any:
        """Postgres uses RETURNING to get the inserted id/row."""
        query, params = self.sql_alchemy_bindings(query, bindings)

        from sqlalchemy import text

        async with self.engine.connect() as conn:
            result = await conn.execute(text(query), params)
            await conn.commit()

            row = result.fetchone()
            if row:
                return dict(zip(result.keys(), row))

        return None
