from typing import TYPE_CHECKING

from fastapi_startkit.masoniteorm import Model
from fastapi_startkit.masoniteorm.relationships import BelongsTo

if TYPE_CHECKING:
    from app.models.post import Post


class Media(Model):
    __table__ = "media"

    id: int
    post_id: int
    url: str

    post: "Post" = BelongsTo("Post")
