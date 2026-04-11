from pydantic import BaseModel, Field as BaseField
from typing import get_type_hints

class User(BaseModel):
    id: int = BaseField()
    name: str
    age: int

types = get_type_hints(User)
from dumpdie import dd
dd(types)
