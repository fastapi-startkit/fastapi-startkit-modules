from fastapi_startkit.masoniteorm import Model
from fastapi_startkit.masoniteorm.relationships import belongs_to

class Media(Model):
    __table__ = "media"
    
    id: int
    post_id: int
    url: str
    
    @belongs_to
    def post(self):
        from .Post import Post
        return Post
