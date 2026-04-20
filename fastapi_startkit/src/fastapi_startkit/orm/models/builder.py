import inspect

import inflection
from typing import TYPE_CHECKING

from dumpdie import dd

from fastapi_startkit.masoniteorm.expressions.expressions import (
    QueryExpression,
    SelectExpression,
    UpdateQueryExpression,
    SubSelectExpression,
    SubGroupExpression,
)
from fastapi_startkit.orm.query.EagerLoadMixin import EagerLoadMixin
from fastapi_startkit.orm.query.support import SupportMixin

if TYPE_CHECKING:
    from fastapi_startkit.orm.connections.connection import Connection


class QueryBuilder(EagerLoadMixin, SupportMixin):
    def __init__(self, connection: 'Connection', grammar, processor):
        super().__init__()
        self.connection = connection
        self.grammar = grammar
        self.processor = processor

        self._columns = []
        self._table = ""
        self._limit = False
        self._wheres = []

        self._sql = ""
        self._bindings = ()

        self._global_scopes = {}
        self._action = "select"

    def set_action(self, action: str) -> 'QueryBuilder':
        self._action = action
        return self

    def set_model(self, model) -> 'QueryBuilder':
        self._model = model
        self._table = model.get_table_name()
        self._global_scopes = model._global_scopes
        return self

    def with_(self, *eagers) -> 'QueryBuilder':
        self._eager_relation.register(eagers)
        return self

    def get_table_name(self) -> str:
        return self._table

    def where_in(self, column: str, values) -> 'QueryBuilder':
        if hasattr(values, '_items'):
            values = values._items
        values = list(values) if not isinstance(values, list) else values
        self._wheres.append(
            QueryExpression(column, "IN", values)
        )
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

    def limit(self, limit: int) -> 'QueryBuilder':
        self._limit = limit
        return self

    async def find(self, primary_key: str|int, columns=None):
        return (
            await self
            .where(self._model.primary_key, primary_key)
            .first(columns)
        )

    async def first(self, columns=None):
        if not columns:
            columns = []

        results = await self.select(columns).limit(1).get()
        return results.first()

    async def get(self, columns=None):
        # TODO: apply scopes
        if not columns:
            columns = []
        return await self.get_models(columns)

    async def get_models(self, columns=None):
        self.select(columns)
        models = await self.connection.select(self.to_qmark(), self.get_bindings())
        collection = self._model.hydrate(models)

        if (
            self._eager_relation.eagers
            or self._eager_relation.nested_eagers
            or self._eager_relation.callback_eagers
        ):
            await self._load_eagers(collection, self._model)

        return collection

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

    async def create(self, attributes: dict):
        model = self._model.new_model_instance(attributes)
        await model.save()

        return model

    async def first_or_create(self, search: dict, attributes: dict | None = None):
        instance = await self.where(search).first()
        if instance is not None:
            return instance

        return await self.create({**(attributes or {}), **search})

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
        updates = [UpdateQueryExpression(col, val) for col, val in values.items()]
        grammar = self.grammar()
        sql = grammar._compile_update(query=self, values=updates, qmark=True).to_sql()
        bindings = list(grammar._bindings)
        return await self.connection.update(sql, bindings)

    def new(self):
        return self.connection.query()

    def where(self, column, *args):
        """Specifies a where expression.

        Arguments:
            column {string} -- The name of the column to search

        Keyword Arguments:
            args {List} -- The operator and the value of the column to search. (default: {None})

        Returns:
            self
        """
        operator, value = self._extract_operator_value(*args)

        if inspect.isfunction(column):
            builder = column(self.new())
            self._wheres += (
                (QueryExpression(None, operator, SubGroupExpression(builder))),
            )
        elif isinstance(column, dict):
            for key, value in column.items():
                self._wheres += ((QueryExpression(key, "=", value, "value")),)
        elif isinstance(value, QueryBuilder):
            self._wheres += (
                (
                    QueryExpression(
                        column, operator, SubSelectExpression(value)
                    )
                ),
            )
        else:
            self._wheres += (
                (QueryExpression(column, operator, value, "value")),
            )
        return self
