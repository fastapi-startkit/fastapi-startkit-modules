from typing import TYPE_CHECKING

from dumpdie import dd

from fastapi_startkit.masoniteorm.expressions.expressions import SelectExpression

if TYPE_CHECKING:
    from connection import Connection

class QueryBuilder:
    def __init__(self, connection: 'Connection', grammar, processor):
        self.connection = connection
        self.grammar = grammar
        self.processor = processor

        self._columns = []
        self._limit = False

        self._sql = ""
        self._bindings = ()

        self._model = None
        self._global_scopes = {}

        self._action = "select"

    def set_action(self, action):
        self._action = action
        return self

    def set_model(self, model):
        self._model = model
        self._global_scopes = model._global_scopes
        if model.__with__:
            self.with_(model.__with__)

        return self

    def with_(self, *eagers):
        # self._eager_relation.register(eagers)
        return self

    def select(self, *args)->'QueryBuilder':
        for arg in args:
            if isinstance(arg, list):
                for column in arg:
                    self._columns += (SelectExpression(column),)
            else:
                for column in arg.split(","):
                    self._columns += (SelectExpression(column),)

        return self

    async def first(self, columns=None):
        if not columns:
            columns = []

        results = await self.select(columns).limit(1).get()

    def limit(self, limit: int)->'QueryBuilder':
        self._limit = limit

        return self

    async def get(self, columns: list=None):
        if not columns:
            columns = []
        self.select(columns)

        result = await self.connection.select(self.to_qmark(), self.get_bindings())
        dd(result)

    def get_bindings(self)->tuple:
        return self._bindings

    def run_scopes(self):
        for name, scope in self._global_scopes.get(self._action, {}).items():
            scope(self)

        return self

    def get_grammar(self):
        # Either _creates when creating, otherwise use columns
        # columns = self._creates or self._columns
        # if not columns and not self._aggregates and self._model:
        #     self.select(*self._model.get_selects())
        #     columns = self._columns

        return self.grammar(
            columns=self._columns,
            # table=self._table,
            # wheres=self._wheres,
            limit=self._limit,
            # offset=self._offset,
            # updates=self._updates,
            # aggregates=self._aggregates,
            # order_by=self._order_by,
            # group_by=self._group_by,
            # distinct=self._distinct,
            # lock=self.lock,
            # joins=self._joins,
            # having=self._having,
        )

    def to_qmark(self):
        """Compiles the QueryBuilder class into a Qmark SQL statement.

        Returns:
            self
        """

        self.run_scopes()
        grammar = self.get_grammar()
        sql = grammar.compile(self._action, qmark=True).to_sql()

        self._bindings = grammar._bindings

        return sql



