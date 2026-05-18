from typing import Optional

from fastapi_startkit.masoniteorm.models.caster import Attribute


class Address(Attribute):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None