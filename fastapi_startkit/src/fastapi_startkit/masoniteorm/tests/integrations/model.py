from dataclasses import dataclass, asdict
from enum import StrEnum

from fastapi_startkit.carbon import Carbon
from fastapi_startkit.masoniteorm import Model
from fastapi_startkit.masoniteorm.models.fields import Field


@dataclass
class Address:
    city: str = None
    country: str = None
    street: str = None

    def get(self, value):
        import json
        if isinstance(value, str):
            value = json.loads(value)

        return Address(
            city=value.get("city"),
            country=value.get("country"),
            street=value.get("street")
        )

    def set(self, value):
        import json
        if isinstance(value, Address):
            return json.dumps(asdict(value))
        return json.dumps(value)

class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class User(Model):
    __primary_key__ = "id"
    __table__ = "users"
    __casts__ = {
        'metadata': 'json',
    }

    id: int
    name: str
    age: int
    balance: float
    metadata: dict
    is_active: bool
    bio: str
    price: float

    # created_at: Date
    gender: Gender
    address: Address
