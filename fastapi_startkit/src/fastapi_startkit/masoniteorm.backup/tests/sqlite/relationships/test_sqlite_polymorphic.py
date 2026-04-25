import pytest_asyncio
from fastapi_startkit.masoniteorm.tests.integrations.config.database import DB

from fastapi_startkit.masoniteorm.connections.sqlite_connection import SQLiteConnection
from fastapi_startkit.masoniteorm.models import Model
from fastapi_startkit.masoniteorm.relationships import BelongsTo, MorphTo
from fastapi_startkit.masoniteorm.schema import Schema
from fastapi_startkit.masoniteorm.schema.platforms import SQLitePlatform


class Profile(Model):
    __table__ = "profiles"
    __connection__ = "dev"


class Logo(Model):
    __table__ = "logos"
    __connection__ = "dev"


class Articles(Model):
    __table__ = "articles"
    __connection__ = "dev"

    logo: "Logo" = BelongsTo("Logo", "id", "article_id")


class Like(Model):
    __connection__ = "dev"

    record: "Like" = MorphTo("Like", "record_type", "record_id")


class User(Model):
    __connection__ = "dev"

    _eager_loads = ()


DB.morph_map({"user": User, "article": Articles})


class TestRelationships:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        # Reset shared engine cache so each test class gets a fresh in-memory DB.
        SQLiteConnection._shared_engines.clear()

        self.schema = Schema(
            connection="dev",
            platform=SQLitePlatform,
            config_path="fastapi_startkit/masoniteorm/tests/integrations/config/database",
        ).on("dev")

        async with await self.schema.create_table_if_not_exists("users") as table:
            table.integer("id").primary()
            table.string("name")

        async with await self.schema.create_table_if_not_exists("articles") as table:
            table.integer("id").primary()
            table.string("title")

        async with await self.schema.create_table_if_not_exists("likes") as table:
            table.integer("id").primary()
            table.string("record_type")
            table.integer("record_id")

        await (
            User()
            .get_builder()
            .bulk_create(
                [
                    {"id": 1, "name": "Alice"},
                    {"id": 2, "name": "Bob"},
                ]
            )
        )

        await (
            Articles()
            .get_builder()
            .bulk_create(
                [
                    {"id": 1, "title": "First Article"},
                    {"id": 2, "title": "Second Article"},
                ]
            )
        )

        await (
            Like()
            .get_builder()
            .bulk_create(
                [
                    {"id": 1, "record_type": "user", "record_id": 1},
                    {"id": 2, "record_type": "user", "record_id": 2},
                    {"id": 3, "record_type": "article", "record_id": 1},
                    {"id": 4, "record_type": "article", "record_id": 2},
                ]
            )
        )

        yield

        await self.schema.drop_table_if_exists("likes")
        await self.schema.drop_table_if_exists("articles")
        await self.schema.drop_table_if_exists("users")
        SQLiteConnection._shared_engines.clear()

    async def test_can_get_polymorphic_relation(self):
        likes = await Like.get()
        for like in likes:
            record = await like.record
            assert isinstance(record, (Articles, User))

    async def test_can_get_eager_load_polymorphic_relation(self):
        likes = await Like.with_("record").get()
        for like in likes:
            assert isinstance(like.record, (Articles, User))
