from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from fastapi_startkit.orm.models.builder import QueryBuilder


class Connection:
    def __init__(self, connection: AsyncEngine, config: dict):
        self.config = config
        self.conn: AsyncEngine = connection

    def query(self) -> 'QueryBuilder':
        return QueryBuilder(
            connection=self,
            grammar=self.get_query_grammar(),
            processor=self.get_post_processor()
        )

    def get_query_grammar(cls):
        pass

    def get_post_processor(self):
        pass

    @classmethod
    def on(cls, connection: str) -> 'Connection':
        return cls(connection)

    async def begin_transaction(self) -> None:
        self.conn = await self.engine.connect()

    async def commit_transaction(self) -> None:
        if self.conn:
            await self.conn.commit()
            await self.conn.close()
            self.conn = None

    async def rollback(self) -> None:
        if self.conn:
            await self.conn.rollback()
            await self.conn.close()
            self.conn = None

    async def reconnect(self) -> None:
        self.conn = await self.engine.connect()

    def sql_alchemy_bindings(self, query: str, bindings: list | None = None):
        params = {}
        if bindings:
            for i, val in enumerate(bindings):
                name = f'p{i}'
                params[name] = val
                query = query.replace('?', f':{name}', 1)
        return (query, params)

    async def run(self, query: str, bindings: list | None = None):
        query, bindings = self.sql_alchemy_bindings(query, bindings)

        async with self.conn.connect() as conn:
            return await conn.execute(text(query), bindings or {})

    async def statement(self, query: str, bindings: list | None = None) -> bool:
        await self.run(query, bindings)
        return True

    async def insert(self, query: str, bindings: list | None = None) -> int | None:
        query, params = self.sql_alchemy_bindings(query, bindings)

        async with self.conn.connect() as conn:
            result = await conn.execute(text(query), params)
            await conn.commit()

        return result.lastrowid

    async def update(self, query: str, bindings: list | None = None) -> int:
        query, params = self.sql_alchemy_bindings(query, bindings)

        async with self.conn.connect() as conn:
            result = await conn.execute(text(query), params)
            await conn.commit()

        return result.rowcount # type: ignore[return-value]

    async def delete(self, query: str, bindings:  list | None = None) -> int:
        result = await self.run(query, bindings)
        return result.rowcount  # type: ignore[return-value]

    async def select(self, query: str, bindings: list | None = None) -> list[dict]:
        result = await self.run(query, bindings)
        keys = result.keys()
        return [dict(zip(keys, row)) for row in result.fetchall()]

    async def select_one(self, query: str, bindings: list | None = None) -> dict | None:
        result = await self.run(query, bindings)
        row = result.fetchone()
        return dict(zip(result.keys(), row)) if row else None
