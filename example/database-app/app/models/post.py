from typing import TYPE_CHECKING
from fastapi_startkit.masoniteorm import Model
from fastapi_startkit.masoniteorm.relationships import BelongsTo, HasMany, BelongsToMany

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.media import Media
    from app.models.tag import Tag

class Post(Model):
    __table__ = "posts"

    id: int
    user_id: int
    title: str
    content: str

    author: "User" = BelongsTo("User", local_key="user_id")
    media: list["Media"] = HasMany("Media")
    tags: list["Tag"] = BelongsToMany("Tag")
