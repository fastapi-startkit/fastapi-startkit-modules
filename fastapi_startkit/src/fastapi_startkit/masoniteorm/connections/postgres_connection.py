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
