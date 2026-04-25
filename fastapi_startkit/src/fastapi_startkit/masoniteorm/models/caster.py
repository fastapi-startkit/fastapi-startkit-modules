import json
import pendulum
import datetime
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, get_type_hints, Optional
from pydantic.fields import FieldInfo
from fastapi_startkit.carbon import Carbon

if TYPE_CHECKING:
    from .model import Model


@dataclass
class BaseCast:
    """Base class for all casters"""

    config: Optional[FieldInfo] = field(default=None, kw_only=True)

    def get(self, value):
        """
        Cast the value to assign to the model attribute
        """
        return value

    def set(self, value):
        """
        Cast the value for use in insert/update queries
        """
        return value


class BoolCast(BaseCast):
    """Casts a value to a boolean"""

    def get(self, value):
        return bool(value)

    def set(self, value):
        return bool(value)


class JsonCast(BaseCast):
    """Casts a value to JSON"""

    def get(self, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except ValueError:
                return None

        return value

    def set(self, value):
        if isinstance(value, str):
            # make sure the string is valid JSON
            json.loads(value)
            return value

        return json.dumps(value, default=str)


class IntCast(BaseCast):
    """Casts a value to an int"""

    def get(self, value):
        return int(value)

    def set(self, value):
        return int(value)


class FloatCast(BaseCast):
    """Casts a value to a float"""

    def get(self, value):
        return float(value)

    def set(self, value):
        return float(value)


class DateCast(BaseCast):
    """Casts a value to a date or datetime"""

    def get(self, value):
        if not value:
            return None

        dt = pendulum.parse(str(value))

        # Return the rich object for attribute access
        return dt

    def set(self, value):
        if not value:
            return None

        return pendulum.parse(str(value)).to_datetime_string()


class DecimalCast(BaseCast):
    """Casts a value to Decimal for accuracy"""

    def get(self, value):
        return Decimal(str(value))

    def set(self, value):
        return str(value)


class Caster:
    casts = {}

    cast_class_map = {
        "bool": BoolCast,
        "json": JsonCast,
        "int": IntCast,
        "float": FloatCast,
        "date": DateCast,
        "decimal": DecimalCast,
    }

    IGNORE_CASTS = ["caster", "db_manager"]

    def __init__(self, model: "Model", casts: dict | None = None):
        self.model = model
        self.casts = Caster.build_casts(model)
        self.casts.update(casts or {})

    @classmethod
    def build_casts(cls, model):
        model = model if isinstance(model, type) else model.__class__
        from .registry import Registry
        from fastapi_startkit.masoniteorm.relationships.BaseRelationship import BaseRelationship

        try:
            annotations = get_type_hints(model)
        except NameError:
            annotations = {}
            for klass in reversed(model.__mro__):
                for name, hint in vars(klass).get("__annotations__", {}).items():
                    if not isinstance(getattr(model, name, None), BaseRelationship):
                        annotations[name] = hint

        annotations = {
            k: v for k, v in annotations.items() if not isinstance(getattr(model, k, None), BaseRelationship)
        }

        # Ignore the builder
        annotations = {k: v for k, v in annotations.items() if k not in cls.IGNORE_CASTS}
        from .fields import FieldDescriptor

        # 1. Collect all potential fields (annotations + descriptors)
        all_field_names = set(annotations.keys())
        descriptors = {}
        for name, attr in cls.__dict__.items():
            if isinstance(attr, FieldDescriptor):
                all_field_names.add(name)
                descriptors[name] = attr

        casts = {}
        for field_name in all_field_names:
            # 2. Get Type Hint and FieldInfo
            typ = annotations.get(field_name) or "str"
            descriptor = descriptors.get(field_name, None)
            field_info = descriptor.field_info if isinstance(descriptor, FieldDescriptor) else None

            caster = Caster.normalize_type(typ)
            if caster in Caster.cast_class_map:
                casts[field_name] = cls.cast_class_map[caster](config=field_info)
            else:
                casts[field_name] = caster

        return casts

    @staticmethod
    def normalize_type(t):
        if t is int:
            return "int"
        if t is str:
            return "str"
        if t is float:
            return "float"
        if t is bool:
            return "bool"
        if t is dict or t is list:
            return "json"
        if t is pendulum.DateTime or t is datetime.datetime or t is datetime.date or t is Carbon:
            return "date"
        if isinstance(t, type):
            if issubclass(t, Enum) or hasattr(t, "get") or hasattr(t, "set"):
                return t

        return "str"

    def get(self, attribute: str, value: Any) -> Any:
        if attribute not in self.casts:
            return value

        cast = self.casts[attribute]

        if cast == "str":
            return str(value) if value is not None else None

        if isinstance(cast, BaseCast):
            return cast.get(value)

        if isinstance(cast, type):
            if issubclass(cast, Enum):
                return cast(value) if value is not None else None
            # Fallback for old custom types that don't inherit BaseCast
            if hasattr(cast, "get"):
                return cast().get(value)
            return cast(value)

        return value

    def set(self, attribute: str, value: Any) -> Any:
        if attribute not in self.casts:
            return value

        cast = self.casts[attribute]

        if isinstance(cast, BaseCast):
            return cast.set(value)

        if isinstance(cast, type):
            # Fallback for old custom types that don't inherit BaseCast
            if hasattr(cast, "set"):
                return cast().set(value)

        return value
