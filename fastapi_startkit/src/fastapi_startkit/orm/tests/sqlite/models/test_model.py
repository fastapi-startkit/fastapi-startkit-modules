import pendulum

from fastapi_startkit.orm.tests.sqlite.test_case import TestCase
from fastapi_startkit.orm.tests.sqlite.model import User


class TestModel(TestCase):
    async def test_create_user(self):
        user = User(name="Test User", email="test@example.com", email_verified_at=pendulum.now())
        await user.save()
        assert user.email == "test@example.com"
        assert user.email_verified_at is not None
