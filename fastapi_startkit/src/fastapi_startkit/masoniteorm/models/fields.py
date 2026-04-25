from typing import Any

from pydantic import Field as BaseField
from pydantic.fields import FieldInfo

from fastapi_startkit.masoniteorm.models.observer import CreatedAtObserver, UpdatedAtObserver


class FieldDescriptor:
    """
    A descriptor that wraps Pydantic's FieldInfo.
    It allows us to store metadata that the Caster can later discover.
    """

    def __init__(self, field_info: FieldInfo):
        self.field_info = field_info
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            # When accessed on the class (e.g., User.name), return the FieldInfo
            return self.field_info

        # When accessed on the instance (e.g., user.name), retrieve from ORM storage
        return instance.get_attribute(self.name)

    def __set__(self, instance, value):
        # When setting (e.g., user.name = 'Joe'), update ORM storage
        instance.set_value(self.name, value)


def Field(*args, **kwargs) -> Any:
    """
    Factory function that returns a FieldDescriptor wrapping a Pydantic Field.
    """
    return FieldDescriptor(BaseField(*args, **kwargs))


class DateTimeField:
    def __init__(self, fmt: str = "YYYY-MM-DD HH:mm:ss", tz: str = "UTC"):
        self.format = fmt
        self.tz = tz

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.get_attribute(self.name)

    # def __set__(self, instance, value):
    #     instance.set_attribute(self.name, value)


class CreatedAtField:
    def __init__(self, fmt: str = "YYYY-MM-DD HH:mm:ss", tz: str = "UTC"):
        self.format = fmt
        self.tz = tz

    def __set_name__(self, owner, name):
        self.name = name
        owner.observe(CreatedAtObserver(name, self.format, self.tz))

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.get_attribute(self.name)

    # def __set__(self, instance, value):
    #     instance.set_value(self.name, value)


class UpdatedAtField:
    def __init__(self, fmt: str = "YYYY-MM-DD HH:mm:ss", tz: str = "UTC"):
        self.format = fmt
        self.tz = tz

    def __set_name__(self, owner, name):
        self.name = name
        owner.observe(UpdatedAtObserver(name, self.format, self.tz))

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.get_attribute(self.name)

    def __set__(self, instance, value):
        instance.set_value(self.name, value)
