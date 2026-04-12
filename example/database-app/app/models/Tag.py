from fastapi_startkit.masoniteorm import Model
from fastapi_startkit.masoniteorm.relationships import belongs_to_many

class Tag(Model):
    __table__ = "tags"
    
    id: int
    name: str
    
    @belongs_to_many
    def posts(self):
        from .Post import Post
        return Post
