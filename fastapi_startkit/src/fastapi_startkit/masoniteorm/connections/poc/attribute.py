from typing import TYPE_CHECKING

from fastapi_startkit.masoniteorm.models.caster import Caster

if TYPE_CHECKING:
    from fastapi_startkit.masoniteorm.connections.poc.database_manager import Model

class Attribute:
    IGNORE_ATTRIBUTES = [
        'db_manager'
    ]

    __casts__ = {}

    caster: Caster = None

    def __init__(self, attributes: dict = None, **kwargs):
        model: 'Model' = self.__class__
        self.caster = Caster(model)

        self._attributes = attributes or {}
        self._dirty_attributes = {}

        for key, value in kwargs.items():
            self.set_attribute(key, value)

    def set_attribute(self, key: str, value):
        if key in self.__casts__:
            value = self.caster.set(key, value)

        if not key.startswith("_"):
            self.__dict__["_dirty_attributes"].update({key: value})

    def get_attribute(self, key: str):
        value = None

        if "_dirty_attributes" in self.__dict__ and key in self.__dict__["_dirty_attributes"]:
            value = self.__dict__["_dirty_attributes"][key]

        if "_attributes" in self.__dict__ and key in self.__dict__["_attributes"]:
            value = self.__dict__["_attributes"][key]

        return self.caster.get(key, value)



