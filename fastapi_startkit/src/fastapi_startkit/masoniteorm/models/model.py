from typing import TypeVar, Type

from inflection import tableize

from ..config import load_config
from ..query import AsyncQueryBuilder

T = TypeVar("T", bound="Model")

class Model:
    __dry__ = False
    __table__ = None
    __connection__ = "default"
    __resolved_connection__ = None
    __selects__ = []

    __observers__ = {}
    __has_events__ = True

    _booted = False
    _scopes = {}
    __primary_key__ = "id"
    __primary_key_type__ = "int"
    __hidden__ = []
    __relationship_hidden__ = {}
    __visible__ = []
    __timestamps__ = True
    __timezone__ = "UTC"
    __with__ = ()
    __force_update__ = False

    date_created_at: str = "created_at"
    date_updated_at: str = "updated_at"

    builder: AsyncQueryBuilder

    """
    Pass through will pass any method calls to the model directly through to the query builder.
    Anytime one of these methods are called on the model it will actually be called on the query builder class.
    """
    __passthrough__ = {
        "add_select",
        "aggregate", "all", "avg", "between", "bulk_create", "chunk", "count", "decrement", "delete", "distinct", "doesnt_exist", "doesnt_have", "exists", "find_or",
        "find_or_404", "first_or_fail", "first", "first_where", "first_or_create", "force_update", "from_", "from_raw", "get", "get_table_schema", "group_by_raw", "group_by", "has",
        "having", "having_raw", "increment", "in_random_order", "join_on", "join", "joins", "last", "left_join", "limit", "lock_for_update", "make_lock", "max", "min",
        "new_from_builder", "new", "not_between", "offset", "on", "or_where", "or_where_null", "order_by_raw", "order_by", "paginate", "right_join", "select_raw", "select",
        "set_global_scope", "set_schema", "shared_lock", "simple_paginate", "skip", "statement", "sum", "table_raw", "take", "to_qmark", "to_sql", "truncate", "update", "when",
        "where_between", "where_column", "where_date", "or_where_doesnt_have", "or_has", "or_where_has", "or_doesnt_have", "or_where_not_exists", "or_where_date", "where_exists",
        "where_from_builder", "where_has", "where_in", "where_like", "where_not_between", "where_not_in", "where_not_like", "where_not_null", "where_null", "where_raw",
        "without_global_scopes", "where", "where_doesnt_have", "with_", "with_count", "latest", "oldest", "value"
    }

    def boot(self):
        if not self._booted:
            # TODO implement observers
            self._booted = True

    def __init__(self):
        super().__init__()
        self.__attributes__ = {}
        self.__original_attributes__ = {}
        self.__dirty_attributes__ = {}
        if not hasattr(self, "__appends__"):
            self.__appends__ = []
        self._relationships = {}
        self._global_scopes = {}

        self.boot()

    def __getattr__(self, attribute):
        if attribute in self.__attributes__:
            return self.__attributes__[attribute]

        if attribute in self.__passthrough__:
            def method(*args, **kwargs):
                return getattr(self.get_builder(), attribute)(*args, **kwargs)
            return method

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{attribute}'"
        )

    def __setattr__(self, key, value):
        if key.startswith("_") or key in self.__dict__ or key in self.__class__.__dict__:
            return super().__setattr__(key, value)

        self.__attributes__[key] = value
        self.__dirty_attributes__[key] = value

    def get_builder(self):
        if hasattr(self, "builder"):
            return self.builder

        self.builder = AsyncQueryBuilder(
            connection=self.__connection__,
            table=self.get_table_name(),
            connection_details=self.get_connection_details(),
            model=self,
            scopes=self._scopes.get(self.__class__),
            dry=self.__dry__,
        )

        return self.builder

    @classmethod
    def get_table_name(cls):
        """Gets the table name.

        Returns:
            str
        """
        return cls.__table__ or tableize(cls.__name__)

    def get_connection_details(self):
        resolver = load_config().DB
        return resolver.get_connection_details()

    def get_primary_key(self):
        return self.__primary_key__

    def get_primary_key_value(self):
        return self.__attributes__.get(self.get_primary_key())

    def is_loaded(self):
        return bool(self.__attributes__)

    def hydrate(self, result):
        if isinstance(result, list):
            return [self.hydrate(r) for r in result]

        model = self.__class__()
        
        # Apply reverse casts
        casts = getattr(self, "__casts__", {})
        hydrated_result = result.copy()
        for key, cast_type in casts.items():
            if key in hydrated_result and hydrated_result[key] is not None:
                if cast_type == "json":
                    import json
                    if isinstance(hydrated_result[key], str):
                        try:
                            hydrated_result[key] = json.loads(hydrated_result[key])
                        except Exception:
                            pass
        
        model.__attributes__.update(hydrated_result)
        model.__original_attributes__.update(hydrated_result)
        return model

    def fill(self, attributes):
        self.__attributes__.update(attributes)
        return self

    def filter_mass_assignment(self, attributes):
        return attributes

    def cast_values(self, attributes):
        casts = getattr(self, "__casts__", {})
        for key, cast_type in casts.items():
            if key in attributes and attributes[key] is not None:
                if cast_type == "json":
                    import json
                    if not isinstance(attributes[key], str):
                        attributes[key] = json.dumps(attributes[key])
        return attributes

    def observe_events(self, instance, event):
        pass

    def get_dirty_attributes(self):
        return self.__dirty_attributes__

    def get_selects(self):
        return self.__selects__


    @classmethod
    async def find(cls: Type[T], record_id: int | str, query=False) -> T:
        return await cls().get_builder().find(record_id, query=query)

    @classmethod
    async def first(cls: Type[T]) -> T:
        return await cls().get_builder().first()

    @classmethod
    def where(cls, *args, **kwargs):
        return cls().get_builder().where(*args, **kwargs)

    @classmethod
    def limit(cls, amount):
        return cls().get_builder().limit(amount)

    @classmethod
    def order_by(cls, column, direction="ASC"):
        return cls().get_builder().order_by(column, direction)

    @classmethod
    def select(cls, *columns):
        return cls().get_builder().select(*columns)

    @classmethod
    def on(cls, connection):
        return cls().get_builder().on(connection)

    @classmethod
    async def create(cls, dictionary=None, **kwargs):
        return await cls().get_builder().create(dictionary, **kwargs)
