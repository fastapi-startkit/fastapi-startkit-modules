from fastapi_startkit.masoniteorm.models import Model

class PostTag(Model):
    __table__ = "post_tag"
    __timestamps__ = False

    id: int
    post_id: int
    tag_id: int
