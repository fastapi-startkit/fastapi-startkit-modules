from typing import TypeVar, Type

from inflection import tableize

import logging
from .caster import Caster
from ..config import load_config
from ..query import AsyncQueryBuilder
from ..collection.Collection import Collection

T = TypeVar("T", bound="Model")


class Model:
    __dry__ = False
    __table__ = None
    __connection__ = "default"
    __resolved_connection__ = None
    __selects__ = []
    __casts__ = {}

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
        self.__attributes__ = {}
        self.__original_attributes__ = {}
        self.__dirty_attributes__ = {}
        if not hasattr(self, "__appends__"):
            self.__appends__ = []
        self._relationships = {}
        self._global_scopes = {}

        self.caster = Caster(self, self.__casts__)

        self.boot()

    def __getattr__(self, attribute):
        """Magic method that is called when an attribute does not exist on the model.

        Args:
            attribute (string): the name of the attribute being accessed or called.

        Returns:
            mixed: Could be anything that a method can return.
        """

        new_name_accessor = "get_" + attribute + "_attribute"

        if new_name_accessor in self.__class__.__dict__:
            return self.__class__.__dict__.get(new_name_accessor)(self)

        if "__dirty_attributes__" in self.__dict__ and attribute in self.__dict__["__dirty_attributes__"]:
            return self.get_dirty_value(attribute)

        if "__attributes__" in self.__dict__ and attribute in self.__dict__["__attributes__"]:
            return self.get_value(attribute)

        if attribute in self.__passthrough__:
            def method(*args, **kwargs):
                return getattr(self.get_builder(), attribute)(*args, **kwargs)
            return method

        if attribute in self.__dict__.get("_relationships", {}):
            return self.__dict__["_relationships"][attribute]

        if attribute not in self.__dict__:
            name = self.__class__.__name__
            raise AttributeError(f"class model '{name}' has no attribute {attribute}")
        return None

    def get_value(self, attribute: str):
        value = self.__attributes__[attribute]
        return self.caster.get(attribute, value)

    def get_dirty_value(self, attribute: str):
        value = self.__dirty_attributes__[attribute]
        return self.caster.get(attribute, value)

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

    def add_relation(self, relations):
        self._relationships.update(relations)
        return self

    @classmethod
    def hydrate(cls, result, relations=None):
        """Takes a result and loads it into a model

        Args:
            result ([type]): [description]
            relations (dict, optional): [description]. Defaults to {}.

        Returns:
            [type]: [description]
        """
        relations = relations or {}

        if result is None:
            return None

        if isinstance(result, (list, tuple)):
            response = []
            for element in result:
                response.append(cls.hydrate(element))
            return cls.new_collection(response)

        elif isinstance(result, dict):
            model = cls()
            dic = {}
            for key, value in result.items():
                # if key in model.get_dates() and value:
                #     value = model.get_new_date(value)
                dic.update({key: value})

            logger = logging.getLogger("masoniteorm.models.hydrate")
            logger.setLevel(logging.INFO)
            logger.propagate = False
            logger.info(
                f"Hydrating Model {cls.__name__}",
                extra={"class_name": cls.__name__, "class_module": cls.__module__},
            )

            model.observe_events(model, "hydrating")
            model.__attributes__.update(dic or {})
            model.__original_attributes__.update(dic or {})
            model.add_relation(relations)
            model.observe_events(model, "hydrated")
            return model

        elif hasattr(result, "serialize"):
            model = cls()
            model.__attributes__.update(result.serialize())
            model.__original_attributes__.update(result.serialize())
            return model
        else:
            model = cls()
            model.observe_events(model, "hydrating")
            model.__attributes__.update(dict(result))
            model.__original_attributes__.update(dict(result))
            model.observe_events(model, "hydrated")
            return model

    def fill(self, attributes):
        self.__attributes__.update(attributes)
        return self

    def filter_mass_assignment(self, attributes):
        return attributes

    def cast_values(self, attributes):
        for key, value in attributes.items():
            attributes[key] = self.caster.set(key, value)
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

    @classmethod
    def new_collection(cls, items):
        return Collection(items)

    def serialize(self):
        return self.__attributes__
