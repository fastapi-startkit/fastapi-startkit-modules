import asyncio
from typing import List

from dumpdie import dd

from fastapi_startkit.carbon import Carbon
from fastapi_startkit.masoniteorm.models.fields import DateTimeField
from fastapi_startkit.masoniteorm.relationships import HasMany, HasOne, BelongsTo
from fastapi_startkit.orm.connections.factory import ConnectionFactory
from fastapi_startkit.orm.connections.manager import DatabaseManager
from fastapi_startkit.orm.models import Model

DB = DatabaseManager(ConnectionFactory(), {
    "default": "sqlite",
    "sqlite": {
        "driver": "sqlite",
        "url": "sqlite+aiosqlite:///masonite.sqlite3",
    }
})

Model.db_manager = DB
schema = DB.get_schema_builder()

class User(Model):
    id: int
    name: str
    email: str
    email_verified_at: Carbon = DateTimeField(fmt="%Y-%m-%d %H:%M:%S", tz="UTC")

    posts: List['Post'] = HasMany('Post', local_key='id', foreign_key='user_id')
    profile: 'Profile' = HasOne('Profile', local_key='id', foreign_key='user_id')


class Post(Model):
    id: int
    user_id: int
    title: str
    body: str

    user: 'User' = BelongsTo('User', local_key='user_id', foreign_key='id')


class Profile(Model):
    id: int
    user_id: int
    bio: str


# ── Migrations ────────────────────────────────────────────────────────────────

async def migrate():
    await schema.drop_table_if_exists('users')
    await schema.drop_table_if_exists('posts')
    await schema.drop_table_if_exists('profiles')

    async with await schema.on('default').create("users") as table:
        table.id()
        table.string("name")
        table.string("email").unique()
        table.timestamp('email_verified_at').nullable()
        table.timestamps()

    async with await schema.on('default').create("posts") as table:
        table.id()
        table.integer("user_id")
        table.string("title")
        table.text("body")
        table.timestamps()

    async with await schema.on('default').create("profiles") as table:
        table.id()
        table.integer("user_id").unique()
        table.string("bio")
        table.timestamps()


# ── Seed ──────────────────────────────────────────────────────────────────────

async def seed():
    alice = User(name="Alice", email="alice@example.com")
    await alice.save()

    bob = User(name="Bob", email="bob@example.com")
    await bob.save()

    alice_id = alice.get_attribute("id")
    bob_id   = bob.get_attribute("id")

    await Post(user_id=alice_id, title="Hello World", body="Alice's first post").save()
    await Post(user_id=alice_id, title="Second Post", body="Alice's second post").save()
    await Post(user_id=bob_id,   title="Bob's Post",  body="Bob's only post").save()

    await Profile(user_id=alice_id, bio="Alice is a developer").save()
    await Profile(user_id=bob_id,   bio="Bob is a designer").save()


# ── Demo ──────────────────────────────────────────────────────────────────────

async def main():
    await migrate()
    await seed()

    print("\n" + "="*60)
    print("1. EAGER LOADING — User.with_('posts', 'profile').get()")
    print("="*60)
    # Issues ONE query for users, ONE for posts, ONE for profiles (no N+1)
    users = await User.with_('posts', 'profile').get()
    for user in users:
        name    = user.get_attribute("name")
        posts   = user.posts   # Collection
        profile = user.profile # single Profile model
        bio     = profile.get_attribute("bio") if profile else "—"
        titles  = [p.get_attribute("title") for p in (posts or [])]
        print(f"  {name}  |  bio={bio}  |  posts={titles}")

    print("\n" + "="*60)
    print("2. LAZY LOADING — await user.posts  /  await user.profile")
    print("="*60)
    # Each access fires its own query (N+1 pattern — use eager loading to avoid)
    alice = await User.query().where("name", "Alice").first()
    alice_posts   = await alice.posts    # separate query
    alice_profile = await alice.profile  # separate query
    print(f"  Alice's posts: {[p.get_attribute('title') for p in alice_posts]}")
    print(f"  Alice's bio:   {alice_profile.get_attribute('bio') if alice_profile else '—'}")

    print("\n" + "="*60)
    print("3. COLLECTION.load() — post-query batch loading (Laravel style)")
    print("="*60)
    all_users = await User.get()      # plain fetch, no relations
    await all_users.load('posts')     # batch-load after the fact (1 extra query)
    for user in all_users:
        name  = user.name
        posts = user.posts
        titles = [p.title for p in (posts or [])]
        print(f"  {name}  |  posts={titles}")

    print("\n" + "="*60)
    print("4. BELONGS TO — post → author")
    print("="*60)
    # BelongsTo eager loading: one query for all authors
    posts = await Post.with_('user').get()
    for post in posts:
        title  = post.title
        author = post.user  # single User model
        author_name = author.name if author else "—"
        print(f"  '{title}'  →  author={author_name}")


if __name__ == "__main__":
    asyncio.run(main())
