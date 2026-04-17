import unittest
from fastapi_startkit.carbon import Carbon
from fastapi_startkit.masoniteorm import Field
from fastapi_startkit.masoniteorm.models import Model
from fastapi_startkit.masoniteorm.relationships import BelongsTo, HasMany, HasOne, BelongsToMany
from fastapi_startkit.masoniteorm.tests.integrations.config.database import DB
from fastapi_startkit.masoniteorm.connections.sqlite_connection import SQLiteConnection
from fastapi_startkit.masoniteorm.schema import Schema
from fastapi_startkit.masoniteorm.schema.platforms import SQLitePlatform


class Profile(Model):
    __table__ = "profiles"
    __connection__ = "dev"
    __timestamps__ = False


class Articles(Model):
    __table__ = "articles"
    __connection__ = "dev"
    __timestamps__ = None
    published_date: Carbon = Field(json_schema_extra={"format": "YYYY-MM-DD HH:mm:ss"})

    logo: 'Logo' = BelongsTo('Logo', "id", "article_id")


class Logo(Model):
    __table__ = "logos"
    __connection__ = "dev"
    __timestamps__ = None


class User(Model):
    __table__ = "users"
    __connection__ = "dev"

    _eager_loads = ()

    __casts__ = {"is_admin": "bool"}

    profile: 'Profile' = BelongsTo("Profile", "id", "user_id")
    articles: 'Articles' = HasMany("Articles", "id", "user_id")

    def get_is_admin(self):
        return "You are an admin"


class Store(Model):
    __connection__ = "dev"

    products: 'Product' = BelongsToMany("Product", "store_id", "product_id", "id", "id", with_timestamps=True)
    products_table: 'Product' = BelongsToMany("Product", "store_id", "product_id", "id", "id", table="product_table")
    store_products: 'Product' = BelongsToMany("Product")


class Product(Model):
    __connection__ = "dev"
    __table__ = "products"


class UserHasOne(Model):
    __table__ = "users"

    __connection__ = "dev"

    profile: 'Profile' = HasOne("Profile", "user_id", "user_id")


class TestRelationships(unittest.IsolatedAsyncioTestCase):
    maxDiff = None

    async def asyncSetUp(self):
        # Reset shared engine cache so each test class gets a fresh in-memory DB.
        SQLiteConnection._shared_engines.clear()

        self.schema = Schema(
            connection="dev",
            platform=SQLitePlatform,
            config_path='fastapi_startkit.masoniteorm.tests.integrations.config.database'
        ).on("dev")

        async with (await self.schema.create_table_if_not_exists("profiles")) as table:
            table.integer("id").primary()
            table.string("name")
            table.integer("user_id")

        async with (await self.schema.create_table_if_not_exists("articles")) as table:
            table.integer("id").primary()
            table.string("title")
            table.integer("user_id")
            table.datetime("published_date")

        async with (await self.schema.create_table_if_not_exists("logos")) as table:
            table.integer("id").primary()
            table.integer("article_id")

        async with (await self.schema.create_table_if_not_exists("users")) as table:
            table.integer("id").primary()
            table.string("name")
            table.boolean("is_admin").default(False)
            table.datetime("created_at")
            table.datetime("updated_at")

        async with (await self.schema.create_table_if_not_exists("stores")) as table:
            table.integer("id").primary()
            table.string("name")

        async with (await self.schema.create_table_if_not_exists("products")) as table:
            table.integer("id").primary()
            table.string("name")
            table.datetime("created_at")
            table.datetime("updated_at")

        async with (await self.schema.create_table_if_not_exists("product_table")) as table:
            table.integer("id").primary()
            table.integer("store_id")
            table.integer("product_id")

        # Seed Data
        await User().get_builder().create({"id": 1, "name": "Joe", "is_admin": True})
        await Profile().get_builder().create({"id": 1, "name": "Joe Profile", "user_id": 1})
        await Articles().get_builder().create({"id": 1, "title": "Masonite ORM", "user_id": 1,  "published_date": "2020-01-01 00:00:00"})
        await Logo().get_builder().create({"id": 1, "article_id": 1})

    async def asyncTearDown(self):
        SQLiteConnection._shared_engines.clear()

    async def test_can_access_relationship(self):
        for user in await User.where("id", 1).get():
            profile = await user.profile
            self.assertIsInstance(profile, Profile)

    async def test_can_access_has_many_relationship(self):
        user = await User.where("id", 1).first()
        articles = await user.articles
        self.assertEqual(len(articles), 1)

    async def test_can_access_relationship_multiple_times(self):
        user = await User.where("id", 1).first()
        articles = await user.articles
        self.assertEqual(len(articles), 1)
        articles = await user.articles
        self.assertEqual(len(articles), 1)

    async def test_can_access_relationship_date(self):
        user = await User.with_("articles").where("id", 1).first()
        for article in user.articles:
            logo = await article.logo
            self.assertTrue(logo.published_date.is_past())

    async def test_loading(self):
        users = await User.with_("articles").get()
        for user in users:
            user

    async def test_relationship_has_one_sql(self):
        self.assertEqual(UserHasOne.profile().to_sql(), 'SELECT * FROM "profiles"')

    async def test_loading_with_nested_with(self):
        users = await User.with_("articles", "articles.logo").get()
        for user in users:
            for article in user.articles:
                logo = getattr(article, "logo", None)
                if inspect.isawaitable(logo):
                    logo = await logo
                if logo:
                    pass

    async def test_casting(self):
        users = await User.with_("articles").where("is_admin", True).get()
        for user in users:
            user

    async def test_setting(self):
        users = await User.with_("articles").where("is_admin", True).get()
        for user in users:
            user.name = "Joe"
            user.is_admin = 1
            await user.save()

    async def test_related(self):
        user = await User.first()
        related_query = user.related("profile").where("active", 1).to_sql()
        self.assertEqual(
            related_query,
            'SELECT * FROM "profiles" WHERE "profiles"."user_id" = \'1\' AND "profiles"."active" = \'1\'',
        )

    async def test_associate_records(self):
        DB.begin_transaction("dev")
        user = await User.first()

        articles = [Articles.hydrate({"id": 1, "title": "associate records"})]

        await user.save_many("articles", articles)
        DB.rollback("dev")

    async def test_belongs_to_many(self):
        store = Store.hydrate({"id": 2, "name": "Walmart"})
        products = await store.products
        # Note: the setup didn't seed store/product relations for this specific hydration test
        # but the query should not error.
        self.assertEqual(len(products), 0)

    async def test_belongs_to_eager_many(self):
        store = await Store.with_("products").first()
        # self.assertEqual(len(store.products), 3)
import inspect
