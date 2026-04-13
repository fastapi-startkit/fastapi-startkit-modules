import json
import pendulum
import datetime
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, get_type_hints, Optional
from pydantic.fields import FieldInfo

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
    """Casts a value to a int"""

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
    """Casts a value to a date string"""

    def get(self, value):
        return pendulum.parse(value).to_date_string()

    def set(self, value):
        return pendulum.parse(value).to_date_string()


class DecimalCast(BaseCast):
    """Casts a value to Decimal for accuracy"""

    def get(self, value):
        return Decimal(str(value))

    def set(self, value):
        return str(value)


class Caster:
    casts = {}

    def __init__(self, model: 'Model', casts: dict|None=None):
        self.model = model
        self.casts = Caster.build_casts(model)
        self.casts.update(casts or {})

    @staticmethod
    def build_casts(model):
        cls = model if isinstance(model, type) else model.__class__
        annotations = get_type_hints(cls)
        
        # Internal map of type to Cast Class
        cast_class_map = {
            "bool": BoolCast,
            "json": JsonCast,
            "int": IntCast,
            "float": FloatCast,
            "date": DateCast,
            "decimal": DecimalCast,
        }

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
            typ = annotations.get(field_name)
            descriptor = descriptors.get(field_name) or getattr(cls, field_name, None)
            
            field_info = None
            if isinstance(descriptor, FieldDescriptor):
                field_info = descriptor.field_info
            elif isinstance(descriptor, FieldInfo):
                field_info = descriptor

            # 3. Resolve Cast Type Identifier or Class
            cast_id_or_class = "str"
            if field_info and field_info.json_schema_extra and "cast" in field_info.json_schema_extra:
                cast_id_or_class = field_info.json_schema_extra["cast"]
            elif typ:
                cast_id_or_class = Caster.normalize_type(typ)
            elif field_info and field_info.default is not ...:
                cast_id_or_class = Caster.normalize_type(type(field_info.default))

            # 4. Instantiate the Caster
            if cast_id_or_class in cast_class_map:
                casts[field_name] = cast_class_map[cast_id_or_class](config=field_info)
            elif isinstance(cast_id_or_class, type) and issubclass(cast_id_or_class, BaseCast):
                casts[field_name] = cast_id_or_class(config=field_info)
            elif isinstance(cast_id_or_class, type) and issubclass(cast_id_or_class, Enum):
                casts[field_name] = cast_id_or_class
            else:
                casts[field_name] = cast_id_or_class # fallback to string or type

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
        if t is pendulum.DateTime or t is datetime.datetime or t is datetime.date:
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
