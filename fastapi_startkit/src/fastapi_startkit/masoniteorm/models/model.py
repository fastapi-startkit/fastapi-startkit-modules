import logging
from typing import TypeVar, Type

from inflection import tableize

from fastapi_startkit.carbon import Carbon
from fastapi_startkit.masoniteorm.models.registry import Registry
from fastapi_startkit.masoniteorm.observers import ObservesEvents
from .caster import Caster
from .fields import CreatedAtField, UpdatedAtField
from ..collection.Collection import Collection
from ..config import load_config
from ..query import AsyncQueryBuilder

T = TypeVar("T", bound="Model")


class Model(ObservesEvents):
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

    created_at: Carbon = CreatedAtField(fmt="%Y-%m-%d %H:%M:%S", tz="UTC")
    updated_at: Carbon = UpdatedAtField(fmt="%Y-%m-%d %H:%M:%S", tz="UTC")

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Registry.register(cls)

    @classmethod
    def get_morph_class(cls):
        return cls.__name__

    __primary_key__ = "id"
    __primary_key_type__ = "int"
    __hidden__ = []
    __relationship_hidden__ = {}
    __visible__ = []
    __timestamps__ = True
    __timezone__ = "UTC"
    __with__ = ()
    __force_update__ = False

    builder: AsyncQueryBuilder

    """
    Pass through will pass any method calls to the model directly through to the query builder.
    Anytime one of these methods are called on the model it will actually be called on the query builder class.
    """
    __passthrough__ = {
        "add_select",
        "aggregate", "between", "bulk_create", "chunk", "decrement", "delete", "distinct", "doesnt_have", "find_or",
        "find_or_404", "first_or_fail", "first_where", "force_update", "from_", "from_raw", "get", "get_table_schema", "group_by_raw", "group_by", "has",
        "having", "having_raw", "increment", "in_random_order", "join_on", "join", "joins", "last", "left_join", "lock_for_update", "make_lock",
        "new_from_builder", "new", "not_between", "offset", "or_where", "or_where_null", "order_by_raw", "right_join", "select_raw",
        "set_global_scope", "set_schema", "shared_lock", "skip", "statement", "table_raw", "take", "to_qmark", "to_sql", "truncate", "update", "when",
        "where_between", "where_column", "where_date", "or_where_doesnt_have", "or_has", "or_where_has", "or_doesnt_have", "or_where_not_exists", "or_where_date", "where_exists",
        "where_from_builder", "where_in", "where_like", "where_not_between", "where_not_in", "where_not_like", "where_not_null", "where_null", "where_raw",
        "without_global_scopes", "value"
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

        self.caster = Caster(self)

        self.boot()

    def __getattr__(self, attribute):
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

    def __setattr__(self, name, value):
        """Redirct all attribute assignments to the ORM storage."""
        # 1. Internal/Private attributes or existing dict entries
        if name.startswith("_") or name == "caster" or name == "builder":
            super().__setattr__(name, value)
            return

        # 2. Check for descriptors (like properties or relationship descriptors)
        cls_attr = getattr(self.__class__, name, None)
        if cls_attr and hasattr(cls_attr, "__set__"):
            cls_attr.__set__(self, value)
            return

        # 3. Default: Store in __attributes__ with casting
        self.__attributes__[name] = self.caster.set(name, value)

    def get_value(self, attribute: str):
        value = self.__attributes__[attribute]
        return self.caster.get(attribute, value)

    def get_dirty_value(self, attribute: str):
        value = self.__dirty_attributes__[attribute]
        return self.caster.get(attribute, value)

    def delete_attribute(self, attribute):
        """Remove an attribute from the model's storage."""
        if attribute in self.__attributes__:
            del self.__attributes__[attribute]
        if attribute in self.__original_attributes__:
            del self.__original_attributes__[attribute]
        if attribute in self.__dirty_attributes__:
            del self.__dirty_attributes__[attribute]
        return self

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

    @classmethod
    def get_primary_key(cls):
        return cls.__primary_key__

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

    def get_dirty_attributes(self):
        return self.__dirty_attributes__

    def get_selects(self):
        return self.__selects__

    @classmethod
    async def get(cls):
        return await cls().get_builder().get()

    @classmethod
    async def all(cls):
        return await cls().get_builder().all()

    @classmethod
    def with_(cls, *eagers):
        return cls().get_builder().with_(*eagers)

    @classmethod
    def with_count(cls, relationship, callback=None):
        return cls().get_builder().with_count(relationship, callback)

    @classmethod
    def latest(cls, column="created_at"):
        return cls().get_builder().latest(column)

    @classmethod
    def oldest(cls, column="created_at"):
        return cls().get_builder().oldest(column)

    @classmethod
    def where_in(cls, column: str, wheres):
        return cls().get_builder().where_in(column=column, wheres=wheres)

    @classmethod
    def where_has(cls, relationship, callback):
        return cls().get_builder().where_has(relationship, callback)

    @classmethod
    def where_doesnt_have(cls, relationship, callback):
        return cls().get_builder().where_doesnt_have(relationship, callback)

    @classmethod
    async def count(cls, column=None):
        return await cls().get_builder().count(column)

    @classmethod
    async def sum(cls, column):
        return await cls().get_builder().sum(column)

    @classmethod
    async def avg(cls, column):
        return await cls().get_builder().avg(column)

    @classmethod
    async def min(cls, column):
        return await cls().get_builder().min(column)

    @classmethod
    async def max(cls, column):
        return await cls().get_builder().max(column)

    @classmethod
    async def exists(cls):
        return await cls().get_builder().exists()

    @classmethod
    async def doesnt_exist(cls):
        return await cls().get_builder().doesnt_exist()

    @classmethod
    async def paginate(cls, per_page, page=1):
        return await cls().get_builder().paginate(per_page, page)

    @classmethod
    async def simple_paginate(cls, per_page, page=1):
        return await cls().get_builder().simple_paginate(per_page, page)

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
    async def first_or_create(cls, wheres, creates: dict = None):
        if creates is None:
            creates = {}
        self = cls()
        record = await self.where(wheres).first()
        total = {}
        total.update(creates)
        total.update(wheres)
        if not record:
            return await self.create(total, id_key=cls().get_primary_key())
        return record

    async def get_related(self, relation):
        related = getattr(self.__class__, relation)
        return related

    @classmethod
    def new_collection(cls, items):
        return Collection(items)

    def serialize(self, exclude=None, include=None):
        """Takes the data as a model and converts it into a dictionary.

        Returns:
            dict
        """
        serialized_dictionary = self.__attributes__.copy()

        # prevent using both exclude and include at the same time
        if exclude is not None and include is not None:
            raise AttributeError("Can not define both includes and exclude values.")

        if exclude is not None:
            self.__hidden__ = exclude

        if include is not None:
            self.__visible__ = include

        # prevent using both hidden and visible at the same time
        if self.__visible__ and self.__hidden__:
            raise AttributeError(
                f"class model '{self.__class__.__name__}' defines both __visible__ and __hidden__."
            )

        if self.__visible__:
            new_serialized_dictionary = {
                k: serialized_dictionary[k]
                for k in self.__visible__
                if k in serialized_dictionary
            }
            serialized_dictionary = new_serialized_dictionary
        else:
            for key in self.__hidden__:
                if key in serialized_dictionary:
                    serialized_dictionary.pop(key)

        # for date_column in self.get_dates():
        #     if (
        #             date_column in serialized_dictionary
        #             and serialized_dictionary[date_column]
        #     ):
        #         serialized_dictionary[date_column] = self.get_new_serialized_date(
        #             serialized_dictionary[date_column]
        #         )

        serialized_dictionary.update(self.__dirty_attributes__)

        # The builder is inside the attributes but should not be serialized
        if "builder" in serialized_dictionary:
            serialized_dictionary.pop("builder")

        # Serialize relationships as well
        serialized_dictionary.update(self.relations_to_dict())

        for append in self.__appends__:
            serialized_dictionary.update({append: getattr(self, append)})

        remove_keys = []
        for key, value in serialized_dictionary.items():
            if key in self.__hidden__:
                remove_keys.append(key)
            if hasattr(value, "serialize"):
                value = value.serialize(self.__relationship_hidden__.get(key, []))
            # if isinstance(value, datetime):
            #     value = self.get_new_serialized_date(value)
            if key in self.__casts__:
                value = self._cast_attribute(key, value)

            serialized_dictionary.update({key: value})

        for key in remove_keys:
            serialized_dictionary.pop(key)

        return serialized_dictionary

    def relations_to_dict(self):
        """Converts a models relationships to a dictionary

        Returns:
            [type]: [description]
        """
        new_dic = {}
        for key, value in self._relationships.items():
            if value == {}:
                new_dic.update({key: {}})
            else:
                if value is None:
                    new_dic.update({key: {}})
                    continue
                elif isinstance(value, list):
                    value = Collection(value).serialize()
                elif isinstance(value, dict):
                    pass
                else:
                    value = value.serialize()

                new_dic.update({key: value})

        return new_dic
