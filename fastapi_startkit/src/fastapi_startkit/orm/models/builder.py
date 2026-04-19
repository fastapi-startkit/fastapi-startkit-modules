import inflection
from typing import TYPE_CHECKING

from fastapi_startkit.masoniteorm.expressions.expressions import (
    QueryExpression,
    SelectExpression,
    UpdateQueryExpression,
)

if TYPE_CHECKING:
    from fastapi_startkit.orm.connections.connection import Connection


class QueryBuilder:
    def __init__(self, connection: 'Connection', grammar, processor):
        self.connection = connection
        self.grammar = grammar
        self.processor = processor

        self._columns = []
        self._table = ""
        self._limit = False
        self._wheres = []

        self._sql = ""
        self._bindings = ()

        self._model = None
        self._global_scopes = {}

        self._action = "select"

    def set_action(self, action: str) -> 'QueryBuilder':
        self._action = action
        return self

    def set_model(self, model) -> 'QueryBuilder':
        self._model = model
        self._table = inflection.tableize(model.__class__.__name__)
        self._global_scopes = model._global_scopes
        if model.__with__:
            self.with_(model.__with__)
        return self

    def with_(self, *eagers) -> 'QueryBuilder':
        # self._eager_relation.register(eagers)
        return self

    def select(self, *args) -> 'QueryBuilder':
        for arg in args:
            if isinstance(arg, list):
                for column in arg:
                    self._columns += (SelectExpression(column),)
            else:
                for column in arg.split(","):
                    self._columns += (SelectExpression(column),)
        return self

    def where(self, column: str, value, equality: str = "=") -> 'QueryBuilder':
        self._wheres.append(
            QueryExpression(column, equality, value, "value", "WHERE")
        )
        return self

    def limit(self, limit: int) -> 'QueryBuilder':
        self._limit = limit
        return self

    async def first(self, columns=None):
        if not columns:
            columns = []
        results = await self.select(columns).limit(1).get()

    async def get(self, columns: list = None):
        if not columns:
            columns = []
        self.select(columns)
        result = await self.connection.select(self.to_qmark(), self.get_bindings())
        return result

    def get_bindings(self) -> tuple:
        return self._bindings

    def run_scopes(self) -> 'QueryBuilder':
        for name, scope in self._global_scopes.get(self._action, {}).items():
            scope(self)
        return self

    def get_grammar(self):
        return self.grammar(
            columns=self._columns,
            table=self._table,
            limit=self._limit,
            wheres=self._wheres,
        )

    def to_qmark(self) -> str:
        self.run_scopes()
        grammar = self.get_grammar()
        sql = grammar.compile(self._action, qmark=True).to_sql()
        self._bindings = grammar._bindings
        return sql

    # --- Write operations ---

    async def insert(self, values: dict | list) -> int | None:
        self.set_action("bulk_create")

        if not values:
            return None

        # Single record → treat as a one-item batch
        if isinstance(values, dict):
            values = [values]
        else:
            values = [{k: row[k] for k in sorted(row)} for row in values]

        self._columns = values

        sql = self.to_qmark()
        bindings = [val for row in values for val in row.values()]
        return await self.connection.insert(sql, bindings)

    async def update(self, values: dict) -> int:
        """Compile and execute an UPDATE via the grammar.

        Mirrors the Laravel pattern:
            grammar._compile_update → UPDATE {table} SET {key_equals} {wheres}

        The caller is responsible for setting a WHERE clause via .where() first
        so that the update is scoped correctly.
        """
        updates = [UpdateQueryExpression(col, val) for col, val in values.items()]
        grammar = self.grammar()
        sql = grammar._compile_update(query=self, values=updates, qmark=True).to_sql()
        bindings = list(grammar._bindings)
        return await self.connection.update(sql, bindings)