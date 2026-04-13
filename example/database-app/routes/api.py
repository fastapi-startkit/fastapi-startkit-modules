from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.models.user import User
from app.models.post import Post
public = APIRouter()

@public.get("/")
async def index():
    return {"message": "Welcome to the Database App Example!"}

@public.get("/users")
async def get_users():
    users = await User.first()
    return JSONResponse({
        "id": users.id,
        "name": users.name,
        "email": users.email,
        "created_at": users.created_at.diff_for_humans()
    })

@public.get("/posts")
async def get_posts():
    # Example of fetching posts with relationships
    posts = await Post.with_("author", "tags", "media").get()
    return posts
