from sqlalchemy import text
from .BaseConnection import BaseConnection
from ..query.grammars import SQLiteGrammar, PostgresGrammar, MySQLGrammar, MSSQLGrammar
from ..query.processors import SQLitePostProcessor, PostgresPostProcessor, MySQLPostProcessor, MSSQLPostProcessor
from ..schema.platforms import SQLitePlatform, PostgresPlatform, MySQLPlatform, MSSQLPlatform


class SQLAlchemyConnection(BaseConnection):
    """
    SQLAlchemy Connection class that mimics Masonite ORM connection interface.
    """

    def __init__(
        self,
        name="default",
        full_details=None,
        session_factory=None,
    ):
        self.name = name
        self.full_details = full_details or {}
        self.session_factory = session_factory
        self.open = True
        self.transaction_level = 0
        self._session = None
        self._last_inserted_id = None

    @property
    def lastrowid(self):
        return self._last_inserted_id

    async def make_connection(self):
        """No-op as SQLAlchemy handles connection lazily or via session."""
        return self

    @classmethod
    def get_default_query_grammar(cls):
        return SQLiteGrammar

    @classmethod
    def get_default_platform(cls):
        return SQLitePlatform

    @classmethod
    def get_default_post_processor(cls):
        return SQLitePostProcessor

    def get_cursor(self):
        return self

    async def query(self, query, bindings=(), results="*"):
        from dumpdie import dd
        dd(self._session)
        """Execute a query using SQLAlchemy session."""
        if not self._session:
            self._session = self.session_factory()
            if hasattr(self._session, "__await__"):
                 self._session = await self._session

        # Handle list of queries (common in migrations/blueprints)
        if isinstance(query, list):
            last_result = None
            for q in query:
                last_result = await self.query(q, bindings, results)
            return last_result

        session = self._session

        # If bindings is a tuple/list, we need to convert it to a dict for SQLAlchemy text()
        # because Masonite grammars use '?' for positional bindings.
        if isinstance(bindings, (list, tuple)) and bindings:
            # Simple replacement of '?' with ':p0', ':p1', etc.
            new_query = query
            new_bindings = {}
            for i, val in enumerate(bindings):
                placeholder = f":p{i}"
                new_query = new_query.replace("?", placeholder, 1)
                new_bindings[f"p{i}"] = val

            result = await session.execute(text(new_query), new_bindings)
        else:
            result = await session.execute(text(query), bindings)

        # Store last inserted id for processors
        if hasattr(result, "context") and result.context and getattr(result.context, "isinsert", False):
            try:
                self._last_inserted_id = result.inserted_primary_key[0]
            except Exception:
                pass

        # Auto-commit if not in transaction for non-SELECT queries
        if self.transaction_level == 0 and not query.strip().upper().startswith("SELECT"):
            await session.commit()

        if results == 1:
            try:
                row = result.fetchone()
                return dict(row._mapping) if row else None
            except Exception:
                # For non-SELECT statements (like CREATE/INSERT/UPDATE)
                return None
        else:
            try:
                row_results = result.fetchall()
                return [dict(row._mapping) for row in row_results]
            except Exception:
                # For non-SELECT statements (like CREATE/INSERT/UPDATE)
                return []

    async def begin(self):
        self.transaction_level += 1
        return self

    async def commit(self):
        if self._session and self.transaction_level == 1:
            await self._session.commit()
        self.transaction_level -= 1
        return self

    async def rollback(self):
        if self._session and self.transaction_level == 1:
            await self._session.rollback()
        self.transaction_level -= 1
        return self

    def get_row_count(self):
        return 0


class SQLiteSQLAlchemyConnection(SQLAlchemyConnection):
    @classmethod
    def get_default_query_grammar(cls):
        return SQLiteGrammar

    @classmethod
    def get_default_platform(cls):
        return SQLitePlatform

    @classmethod
    def get_default_post_processor(cls):
        return SQLitePostProcessor


class PostgresSQLAlchemyConnection(SQLAlchemyConnection):
    @classmethod
    def get_default_query_grammar(cls):
        return PostgresGrammar

    @classmethod
    def get_default_platform(cls):
        return PostgresPlatform

    @classmethod
    def get_default_post_processor(cls):
        return PostgresPostProcessor


class MySQLSQLAlchemyConnection(SQLAlchemyConnection):
    @classmethod
    def get_default_query_grammar(cls):
        return MySQLGrammar

    @classmethod
    def get_default_platform(cls):
        return MySQLPlatform

    @classmethod
    def get_default_post_processor(cls):
        return MySQLPostProcessor


class MSSQLSQLAlchemyConnection(SQLAlchemyConnection):
    @classmethod
    def get_default_query_grammar(cls):
        return MSSQLGrammar

    @classmethod
    def get_default_platform(cls):
        return MSSQLPlatform

    @classmethod
    def get_default_post_processor(cls):
        return MSSQLPostProcessor
