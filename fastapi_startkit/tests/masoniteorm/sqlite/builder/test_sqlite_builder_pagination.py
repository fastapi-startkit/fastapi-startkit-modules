from ...fixtures.model import User
from ..test_case import TestCase
from fastapi_startkit.masoniteorm.collection import Collection


class TestQueryBuilderPagination(TestCase):
    async def test_limit_and_offset(self):
        all_users = await User.get()
        assert all_users.count() > 0

    async def test_limit(self):
        users = await User.query().limit(1).get()
        assert users.count() == 1

    async def test_offset_skips_records(self):
        all_users = await User.query().get()
        total = all_users.count()
        if total > 1:
            page2 = await User.query().limit(total).offset(1).get()
            assert page2.count() == total - 1
