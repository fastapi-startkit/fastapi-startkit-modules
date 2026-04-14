from .connection import BaseConnection
from ..query.grammars import SQLiteGrammar
from ..schema.platforms import SQLitePlatform
from ..query.processors import SQLitePostProcessor

class SQLiteConnection(BaseConnection):
    """SQLite implementation of Async SQLAlchemy connection."""

    def get_connection_url(self):
        database = self.connection_details.get("database")
        # Using aiosqlite driver
        return f"sqlite+aiosqlite:///{database}"

    @classmethod
    def get_default_query_grammar(cls):
        return SQLiteGrammar

    @classmethod
    def get_default_platform(cls):
        return SQLitePlatform

    @classmethod
    def get_default_post_processor(cls):
        return SQLitePostProcessor
