from typing import TYPE_CHECKING

from fastapi_startkit.masoniteorm.models import Model
from fastapi_startkit.masoniteorm.relationships import HasMany

if TYPE_CHECKING:
    from app.models.post import Post


class User(Model):
    __table__ = "users"

    id: int
    name: str
    email: str

    posts: list["Post"] = HasMany("Post")
