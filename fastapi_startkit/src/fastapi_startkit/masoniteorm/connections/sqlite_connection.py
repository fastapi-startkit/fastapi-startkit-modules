from fastapi_startkit.masoniteorm.query.grammars import SQLiteGrammar
from fastapi_startkit.masoniteorm.query.processors import SQLitePostProcessor
from fastapi_startkit.masoniteorm.schema.platforms import SQLitePlatform
from .connection import Connection


class SQliteConnection(Connection):
    @classmethod
    def get_query_grammar(cls):
        return SQLiteGrammar

    @classmethod
    def get_default_platform(cls):
        return SQLitePlatform

    @classmethod
    def get_post_processor(cls):
        return SQLitePostProcessor
