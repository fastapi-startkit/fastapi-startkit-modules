import json
import pendulum
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Any, get_type_hints

if TYPE_CHECKING:
    from .model import Model

class BoolCast:
    """Casts a value to a boolean"""

    def get(self, value):
        """
        Cast the value to assign to the model attribute
        """
        return bool(value)

    def set(self, value):
        """
        Cast the value for use in insert/update queries
        """
        return bool(value)


class JsonCast:
    """Casts a value to JSON"""

    def get(self, value):
        """
        Cast the value to assign to the model attribute
        """
        if isinstance(value, str):
            try:
                return json.loads(value)
            except ValueError:
                return None

        return value

    def set(self, value):
        """
        Cast the value for use in insert/update queries
        """
        if isinstance(value, str):
            # make sure the string is valid JSON
            json.loads(value)
            return value

        return json.dumps(value, default=str)


class IntCast:
    """Casts a value to a int"""

    def get(self, value):
        """
        Cast the value to assign to the model attribute
        """
        return int(value)

    def set(self, value):
        """
        Cast the value for use in insert/update queries
        """
        return int(value)


class FloatCast:
    """Casts a value to a float"""

    def get(self, value):
        """
        Cast the value to assign to the model attribute
        """
        return float(value)

    def set(self, value):
        """
        Cast the value for use in insert/update queries
        """
        return float(value)


class DateCast:
    """Casts a value to a float"""

    def get(self, value):
        """
        Cast the value to assign to the model attribute
        """
        return pendulum.parse(value).to_date_string()

    def set(self, value):
        """
        Cast the value for use in insert/update queries
        """
        return pendulum.parse(value).to_date_string()


class DecimalCast:
    """Casts a value to Decimal for accuracy"""

    def get(self, value):
        """
        Cast the value to assign to the model attribute
        """
        return Decimal(str(value))

    def set(self, value):
        """
        Cast the value for use in insert/update queries
        """
        return str(value)


class Caster:
    casts = {}

    def __init__(self, model: 'Model', casts: dict|None=None):
        self.model = model
        self.casts = Caster.build_casts(model)
        self.casts.update(casts or {})

        self.__internal_cast_map__ = {
            "bool": BoolCast(),
            "json": JsonCast(),
            "int": IntCast(),
            "float": FloatCast(),
            "date": DateCast(),
            "decimal": DecimalCast(),
        }

    @staticmethod
    def build_casts(model):
        annotations = get_type_hints(model if isinstance(model, type) else model.__class__)

        return {
            field: Caster.normalize_type(typ)
            for field, typ in annotations.items()
        }

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
        if isinstance(t, type):
            if issubclass(t, Enum) or hasattr(t, "get") or hasattr(t, "set"):
                return t

        return "str"

    def get(self,  attribute: str, value: Any)->Any:
        if attribute not in self.casts:
            return value

        typ = self.casts[attribute]

        if typ == "str":
            return str(value) if value is not None else None

        if typ in self.__internal_cast_map__:
            return self.__internal_cast_map__[typ].get(value)

        if isinstance(typ, type):
            if hasattr(typ, "get"):
                return typ().get(value)
            return typ(value)

        return value

    def set(self, attribute: str, value: Any) -> Any:
        if attribute not in self.casts:
            return value

        typ = self.casts[attribute]

        if typ in self.__internal_cast_map__:
            return self.__internal_cast_map__[typ].set(value)

        if isinstance(typ, type):
            if hasattr(typ, "set"):
                return typ().set(value)

        return value
