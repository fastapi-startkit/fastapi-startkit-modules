from fastapi_startkit.masoniteorm import Model
from fastapi_startkit.masoniteorm.relationships import belongs_to, has_many, belongs_to_many

class Post(Model):
    __table__ = "posts"
    
    id: int
    user_id: int
    title: str
    content: str
    
    @belongs_to
    def author(self):
        from .User import User
        return User
        
    @has_many
    def media(self):
        from .Media import Media
        return Media
        
    @belongs_to_many
    def tags(self):
        from .Tag import Tag
        return Tag
