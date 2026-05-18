from ...fixtures.casts import Address
from ...fixtures.model import User
from ..test_case import TestCase


class SqliteModelCastsTest(TestCase):
    async def test_sqlite_model_casts_int(self):
        user = await User.first()

        # id: int annotation → IntCast
        self.assertIsInstance(user.id, int)

    async def test_sqlite_model_casts_str(self):
        user = await User.first()

        # name: str annotation → str cast
        self.assertIsInstance(user.name, str)

    async def test_sqlite_model_casts_bool_true(self):
        user = await User.first()

        # is_admin: bool annotation → BoolCast; SQLite stores booleans as 0/1
        self.assertIsInstance(user.is_admin, bool)
        self.assertTrue(user.is_admin)

    async def test_sqlite_model_casts_bool_false(self):
        user = await User.where("email", "guest@guest.com").first()

        # A user seeded with is_admin=False should cast to bool False
        self.assertIsInstance(user.is_admin, bool)
        self.assertFalse(user.is_admin)

    async def test_sqlite_model_casts_dict(self):
        user = await User.where("email", "admin@admin.com").first()

        # preferences: dict annotation → JsonCast; stored as JSON string in SQLite
        self.assertIsInstance(user.preferences, dict)
        self.assertEqual(user.preferences["theme"], "dark")
        self.assertEqual(user.preferences["language"], "en")

    async def test_sqlite_model_casts_dict_none(self):
        user = await User.where("email", "guest@guest.com").first()

        # guest user has no preferences seeded — should remain None
        self.assertIsNone(user.preferences)

    async def test_sqlite_model_casts_list(self):
        user = await User.where("email", "admin@admin.com").first()

        # Update preferences to a JSON array and verify list cast on re-fetch
        await user.update({"preferences": ["reading", "coding"]})
        updated = await User.where("email", "admin@admin.com").first()

        self.assertIsInstance(updated.preferences, list)
        self.assertIn("reading", updated.preferences)
        self.assertIn("coding", updated.preferences)

    async def test_sqlite_model_casts_pydantic_object(self):
        user = await User.where("email", "admin@admin.com").first()

        # address: Address annotation → custom Pydantic cast
        # DB stores JSON text, get() deserializes it into an Address instance
        self.assertIsInstance(user.address, Address)
        self.assertEqual(user.address.address, "123 Main St")
        self.assertEqual(user.address.city, "Sydney")
        self.assertEqual(user.address.state, "NSW")
        self.assertEqual(user.address.country, "Australia")

    async def test_sqlite_model_casts_pydantic_object_none(self):
        user = await User.where("email", "guest@guest.com").first()

        # guest user has no address seeded — should remain None
        self.assertIsNone(user.address)

    async def test_sqlite_model_casts_pydantic_object_insert_with_instance(self):
        address = Address(address="456 Queen St", city="Melbourne", state="VIC", country="Australia")

        await User.create({
            "email": "instance@example.com",
            "name": "Instance User",
            "is_admin": False,
            "address": address,
        })

        fetched = await User.where("email", "instance@example.com").first()

        self.assertIsInstance(fetched.address, Address)
        self.assertEqual(fetched.address.address, "456 Queen St")
        self.assertEqual(fetched.address.city, "Melbourne")

    async def test_sqlite_model_casts_pydantic_object_insert_with_dict(self):
        await User.create({
            "email": "dict@example.com",
            "name": "Dict User",
            "is_admin": False,
            "address": {"address": "789 King St", "city": "Brisbane", "state": "QLD", "country": "Australia"},
        })

        fetched = await User.where("email", "dict@example.com").first()

        self.assertIsInstance(fetched.address, Address)
        self.assertEqual(fetched.address.address, "789 King St")
        self.assertEqual(fetched.address.city, "Brisbane")