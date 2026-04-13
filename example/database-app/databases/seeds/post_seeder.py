from fastapi_startkit.logging import Logger
from fastapi_startkit.masoniteorm.seeds import Seeder
from app.models import Post, User, Tag, PostTag


class PostSeeder(Seeder):
    async def run(self):
        user = await User.first()
        if not user:
            return

        # Create tags
        tag_python = await Tag.first_or_create({"name": "Python"})
        tag_fastapi = await Tag.first_or_create({"name": "FastAPI"})
        tag_orm = await Tag.first_or_create({"name": "ORM"})

        # Create First Blog Post
        post1 = await Post.create(
            user_id=user.id,
            title="First Blog Post",
            content="This is the content of the first blog post."
        )
        # Attach tags to first post
        await PostTag.first_or_create({"post_id": post1.id, "tag_id": tag_python.id})
        await PostTag.first_or_create({"post_id": post1.id, "tag_id": tag_fastapi.id})
        # await post1.tags.attach(post1, tag_python)
        # await post1.tags.attach(post1, tag_fastapi)

        # Create Second Blog Post
        post2 = await Post.create(
            user_id=user.id,
            title="Second Blog Post",
            content="This is the content of the second blog post."
        )
        # Attach tags to second post
        await PostTag.first_or_create({"post_id": post2.id, "tag_id": tag_python.id})
        await PostTag.first_or_create({"post_id": post2.id, "tag_id": tag_fastapi.id})
        # await post2.tags.attach(post2, tag_fastapi)
        # await post2.tags.attach(post2, tag_orm)
