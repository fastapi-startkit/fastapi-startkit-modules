from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


class ConnectionResolver:
    """
    SQLAlchemy-based replacement for Masonite ORM ConnectionResolver
    """

    _engines = {}
    _sessions = {}
    _sticky_sessions = {}

    def __init__(self, connection_details=None):
        self._connection_details = connection_details or {}
        self.connection_factory = ConnectionFactory(self)

    # -------------------------
    # CONFIG
    # -------------------------
    def set_connection_details(self, connection_details):
        self._connection_details = connection_details
        return self

    def get_connection_details(self):
        return self._connection_details

    # -------------------------
    # ENGINE CREATION
    # -------------------------
    def _build_url(self, name):
        config = self._connection_details[name]
        driver = config["driver"]

        if driver == "sqlite":
            return f"sqlite+aiosqlite:///{config['database']}"

        if driver == "postgres":
            port = f":{config['port']}" if config.get("port") else ""
            return (
                f"postgresql+asyncpg://{config['user']}:{config['password']}"
                f"@{config['host']}{port}/{config['database']}"
            )

        if driver == "mysql":
            port = f":{config['port']}" if config.get("port") else ""
            return (
                f"mysql+aiomysql://{config['user']}:{config['password']}"
                f"@{config['host']}{port}/{config['database']}"
            )

        raise ValueError(f"Unsupported driver: {driver}")

    def get_engine(self, name="default"):
        if name == "default":
            name = self._connection_details.get("default", "default")

        if name in self._engines:
            return self._engines[name]

        config = self._connection_details[name]

        base_kwargs = {
            "echo": config.get("echo", False),
        }

        if config["driver"] != "sqlite":
            base_kwargs.update(
                {
                    "pool_size": config.get("pool_size", 10),
                    "max_overflow": config.get("max_overflow", 20),
                }
            )

        engine = create_async_engine(self._build_url(name), **base_kwargs)

        self._engines[name] = engine
        return engine

    # -------------------------
    # SESSION FACTORY
    # -------------------------
    def get_session_factory(self, name="default"):
        if name == "default":
            name = self._connection_details.get("default", "default")

        if name in self._sticky_sessions:
            # Return a mock factory that returns the sticky session
            session = self._sticky_sessions[name]

            # Since async_sessionmaker is used as Session(), we return a callable
            async def factory():
                return session

            return factory

        if name in self._sessions:
            return self._sessions[name]

        engine = self.get_engine(name)

        Session = async_sessionmaker(
            engine,
            expire_on_commit=False,
        )

        return Session

    # -------------------------
    # SESSION CONTEXT (Laravel-like DB access)
    # -------------------------
    @asynccontextmanager
    async def connection(self, name="default"):
        """
        Usage:
            async with DB.connection() as session:
                ...
        """
        Session = self.get_session_factory(name)

        async with Session() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    # -------------------------
    # TRANSACTION WRAPPER
    # -------------------------
    @asynccontextmanager
    async def transaction(self, name="default"):
        """
        Usage:
            async with DB.transaction():
                ...
        """
        async with self.connection(name) as session:
            async with session.begin():
                yield session

    # -------------------------
    # GLOBAL ENGINE ACCESS (optional)
    # -------------------------
    def engine(self, name="default"):
        return self.get_engine(name)

    # -------------------------
    # RAW STATEMENT (LIKE YOUR OLD QUERY BUILDER ENTRY POINT)
    # -------------------------
    async def statement(self, query, bindings=(), connection="default"):
        from sqlalchemy import text

        Session = self.get_session_factory(connection)

        async with Session() as session:
            result = await session.execute(text(query), bindings)
            return result.fetchall()

    # -------------------------
    # GLOBAL CLEANUP (optional)
    # -------------------------
    async def dispose(self, name="default"):
        if name in self._engines:
            await self._engines[name].dispose()
            del self._engines[name]

        if name in self._sessions:
            del self._sessions[name]

        from dumpdie import dd
        dd(self._engines)

    # compatibility methods for QueryBuilder
    def get_query_builder(self, connection="default"):
        from ..query import QueryBuilder

        return QueryBuilder(
            connection=connection,
            connection_details=self.get_connection_details(),
        )

    def get_schema_builder(self, connection="default", schema=None):
        from ..schema import Schema

        return Schema(
            connection=connection,
            connection_details=self.get_connection_details(),
            schema=schema,
        )

    def set_sticky_session(self, session, name="default"):
        if name == "default":
            name = self._connection_details.get("default", "default")
        self._sticky_sessions[name] = session

    def remove_sticky_session(self, name="default"):
        if name == "default":
            name = self._connection_details.get("default", "default")
        if name in self._sticky_sessions:
            del self._sticky_sessions[name]


class ConnectionFactory:
    def __init__(self, resolver):
        self.resolver = resolver
        from .SQLAlchemyConnection import (
            SQLiteSQLAlchemyConnection,
            PostgresSQLAlchemyConnection,
            MySQLSQLAlchemyConnection,
            MSSQLSQLAlchemyConnection,
        )

        self.drivers = {
            "sqlite": SQLiteSQLAlchemyConnection,
            "mysql": MySQLSQLAlchemyConnection,
            "postgres": PostgresSQLAlchemyConnection,
            "mssql": MSSQLSQLAlchemyConnection,
        }

    def make(self, driver):
        cls = self.drivers.get(driver)
        if not cls:
            raise ValueError(f"Driver {driver} not supported")

        # Create a subclass that acts as a factory
        # This ensures @classmethods like get_default_platform() still work
        resolver = self.resolver

        class AsyncConnectionFactory(cls):
            def __init__(self, **kwargs):
                name = kwargs.get("name", "default")
                super().__init__(
                    name=name,
                    full_details=kwargs.get("full_details"),
                    session_factory=resolver.get_session_factory(name),
                )

        return AsyncConnectionFactory
