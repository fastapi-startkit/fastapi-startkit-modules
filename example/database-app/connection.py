import asyncio

from dumpdie import dump

from app.models import Post


async def main():
    posts = await Post.with_("author", "tags").get()
    dump([{
    'id': post.id,
    'author': post.author.name,
    'tags': [tag.name for tag in post.tags]
} for post in posts])

if __name__ == "__main__":
    asyncio.run(main())
