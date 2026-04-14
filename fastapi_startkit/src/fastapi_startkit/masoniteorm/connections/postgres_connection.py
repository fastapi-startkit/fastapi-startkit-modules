from .connection import BaseConnection
from ..query.grammars import PostgresGrammar
from ..schema.platforms import PostgresPlatform
from ..query.processors import PostgresPostProcessor


class PostgresConnection(BaseConnection):
    """Postgres implementation of Async SQLAlchemy connection."""
    def get_connection_url(self):
        user = self.connection_details.get("user")
        password = self.connection_details.get("password")
        host = self.connection_details.get("host")
        port = self.connection_details.get("port")
        database = self.connection_details.get("database")
        port_str = f":{port}" if port else ""
        # Using asyncpg driver
        return f"postgresql+asyncpg://{user}:{password}@{host}{port_str}/{database}"

    @classmethod
    def get_default_query_grammar(cls):
        return PostgresGrammar

    @classmethod
    def get_default_platform(cls):
        return PostgresPlatform

    @classmethod
    def get_default_post_processor(cls):
        return PostgresPostProcessor
