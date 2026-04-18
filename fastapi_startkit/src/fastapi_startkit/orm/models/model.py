from fastapi_startkit.carbon import Carbon
from fastapi_startkit.masoniteorm.connections.poc.attribute import Attribute
from fastapi_startkit.masoniteorm.connections.poc.relationship import Relationship
from fastapi_startkit.masoniteorm.models.fields import CreatedAtField, UpdatedAtField
from fastapi_startkit.masoniteorm.observers import ObservesEvents
from fastapi_startkit.orm.connections.manager import DatabaseManager


class Model(Attribute, Relationship, ObservesEvents):
    db_manager: 'DatabaseManager' = None

    __observers__ = {}
    __has_events__ = True

    created_at: Carbon = CreatedAtField(fmt="%Y-%m-%d %H:%M:%S", tz="UTC")
    updated_at: Carbon = UpdatedAtField(fmt="%Y-%m-%d %H:%M:%S", tz="UTC")

    def __init__(self, attributes: dict = None, **kwargs):
        super().__init__(attributes, **kwargs)
        self.connection = 'default'
        self._global_scopes = {}
        self.__with__ = {}

    def new_query(self):
        return self.db_manager.connection(self.connection).query().set_model(self)

    def __getattr__(self, attribute):
        return self.get_attribute(attribute)

    @classmethod
    def query(cls):
        return cls().new_query()
