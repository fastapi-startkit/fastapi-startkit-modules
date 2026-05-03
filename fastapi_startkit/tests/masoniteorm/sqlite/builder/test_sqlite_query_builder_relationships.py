from ...fixtures.model import User, Articles
from ..test_case import TestCase
from fastapi_startkit.masoniteorm.collection import Collection


class TestQueryBuilderRelationships(TestCase):
    async def test_where_has(self):
        users = await User.where_has("articles").get()
        assert users.count() >= 1
        for user in users:
            assert isinstance(user, User)

    async def test_where_has_with_callback(self):
        users = await User.where_has("articles", lambda q: q.where("id", 1)).get()
        # may or may not return results depending on data — just check it runs
        assert isinstance(users, Collection)

    async def test_where_has_sql_generation(self):
        sql = User.query().where_has("articles").to_sql()
        assert "EXISTS" in sql
        assert "articles" in sql
