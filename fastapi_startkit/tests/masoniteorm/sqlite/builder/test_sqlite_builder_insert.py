from ...fixtures.model import User
from ..test_case import TestCase


class TestQueryBuilderInsert(TestCase):
    async def test_insert_creates_record_and_returns_model(self):
        user = await User.create({"email": "insert@test.com", "name": "Insert User", "is_admin": False})
        assert isinstance(user.id, int)
        assert user.name == "Insert User"

    async def test_insert_via_builder(self):
        await User.query().insert({"email": "bulk@test.com", "name": "Bulk User", "is_admin": False})
        user = await User.where("email", "bulk@test.com").first()
        assert user is not None
        assert user.name == "Bulk User"
