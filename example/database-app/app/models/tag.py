from typing import TYPE_CHECKING
from fastapi_startkit.masoniteorm.models import Model
from fastapi_startkit.masoniteorm.relationships import BelongsToMany

if TYPE_CHECKING:
    from app.models.post import Post

class Tag(Model):
    __table__ = "tags"

    id: int
    name: str

    posts: list["Post"] = BelongsToMany("Post")
