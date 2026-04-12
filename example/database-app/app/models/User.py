from fastapi_startkit.masoniteorm import Model
from fastapi_startkit.masoniteorm.relationships import has_many

class User(Model):
    __table__ = "users"
    
    id: int
    name: str
    email: str
    
    @has_many
    def posts(self):
        from .Post import Post
        return Post
