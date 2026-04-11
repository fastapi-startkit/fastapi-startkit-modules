from fastapi_startkit.masoniteorm import Model
from fastapi_startkit.masoniteorm.testing import TestCase


class User(Model):
    __table__ = "users"
    __casts__ = {"metadata": "json"}

    id: int = Field(primary_key=True)
    name: str
    age: int
    balance: float
    metadata: dict
    is_active: bool
    bio: str
    price: float

class TestModel(TestCase):
    migration_directory = "fastapi_startkit/masoniteorm/tests/integrations/databases/migrations"

    async def test_database_is_isolated(self):
        user = await User.first()
        self.assertIsNone(user)

    async def test_first_record_can_be_fetch(self):
        await User.create(name="Joe", username="joe", email="joe@test.com", password="password")

        user = await User.first()
        self.assertEqual(user.name, "Joe")

    async def test_can_create_with_dict(self):
        await User.create({"name": "Jane", "username": "jane", "email": "jane@test.com", "password": "password"})

        user = await User.first()
        self.assertEqual(user.name, "Jane")

    async def test_can_insert_all_types(self):
        data = {
            "name": "All Types",
            "username": "alltypes",
            "email": "all@types.com",
            "password": "password",
            "age": 25,
            "balance": 1000.50,
            "metadata": {"key": "value", "active": True},
            "is_active": True,
            "bio": "A long text for bio...",
            "price": 19.99
        }
        await User.create(data)

        user = await User.where("username", "alltypes").first()
        self.assertEqual(user.name, "All Types")
        self.assertEqual(user.age, 25)
        self.assertEqual(user.balance, 1000.50)

        # Test JSON
        self.assertEqual(user.metadata, {"key": "value", "active": True})

        self.assertTrue(user.is_active)
        self.assertEqual(user.bio, "A long text for bio...")
        self.assertEqual(float(user.price), 19.99)
