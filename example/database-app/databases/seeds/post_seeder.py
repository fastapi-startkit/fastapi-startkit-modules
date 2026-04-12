from fastapi_startkit.masoniteorm.seeds import Seeder
from app.models.Post import Post
from app.models.User import User

class PostSeeder(Seeder):
    async def run(self):
        user = await User.first()
        if user:
            await Post.create(
                user_id=user.id,
                title="First Blog Post",
                content="This is the content of the first blog post."
            )
            await Post.create(
                user_id=user.id,
                title="Second Blog Post",
                content="This is the content of the second blog post."
            )
