from ...fixtures.model import User, Articles, Profile
from ..test_case import TestCase
from fastapi_startkit.masoniteorm.collection import Collection


class TestQueryBuilderEagerLoading(TestCase):
    async def test_with_loads_related_model(self):
        users = await User.with_("profile").get()
        for user in users:
            if user.profile is not None:
                assert hasattr(user.profile, "id")

    async def test_with_first_loads_related(self):
        user = await User.with_("profile").where("id", 1).first()
        assert user is not None

    async def test_with_nested_eager_load(self):
        users = await User.with_("articles").get()
        for user in users:
            if user.articles is not None:
                assert isinstance(user.articles, Collection)
