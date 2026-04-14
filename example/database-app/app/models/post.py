from typing import TYPE_CHECKING

from fastapi_startkit.masoniteorm import Model
from fastapi_startkit.masoniteorm.models import registry
from fastapi_startkit.masoniteorm.relationships import BelongsTo

if TYPE_CHECKING:
    from app.models.user import User


class Post(Model):
    __table__ = "posts"

    id: int
    user_id: int
    title: str
    content: str

    def author(self):
        return registry.Registry.resolve('User')

    author: "User" = BelongsTo(author, local_key='user_id', foreign_key="id")
    # media: list["Media"] = HasMany("Media")
    # tags: list["Tag"] = BelongsToMany("Tag")
