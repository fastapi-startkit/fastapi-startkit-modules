from typing import TYPE_CHECKING

from fastapi_startkit.masoniteorm.models.caster import Caster

if TYPE_CHECKING:
    from fastapi_startkit.orm.connections.manager import Model

class Attribute:
    # Attributes that are model infrastructure, not data columns.
    # Assignments to these bypass set_attribute() and go straight to __dict__.
    _META_ATTRIBUTES = frozenset({"caster", "connection", "db_manager"})

    __casts__ = {}

    caster: Caster = None

    def __init__(self, attributes: dict = None, **kwargs):
        model: 'Model' = self.__class__
        self.caster = Caster(model)

        self._attributes = attributes or {}
        self._dirty_attributes = {}

        for key, value in kwargs.items():
            self.set_attribute(key, value)

    def __setattr__(self, key: str, value):
        # Before _dirty_attributes is initialised (early __init__), or for
        # internal/meta attributes, fall back to normal object assignment.
        if (
            key.startswith("_")
            or key in self._META_ATTRIBUTES
            or "_dirty_attributes" not in self.__dict__
        ):
            super().__setattr__(key, value)
        else:
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

    def is_dirty(self) -> bool:
        return bool(self._dirty_attributes)

    def get_dirty(self) -> dict:
        return dict(self._dirty_attributes)

    def get_attributes_for_insert(self) -> dict:
        return {**self._attributes, **self._dirty_attributes}



