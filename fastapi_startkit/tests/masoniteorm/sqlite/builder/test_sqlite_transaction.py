from ...fixtures.model import User
from ...fixtures.db import DB
from ..test_case import TestCase


class TestQueryBuilderTransaction(TestCase):
    async def test_rollback_undoes_insert(self):
        conn = DB.connection("sqlite")
        await conn.begin_transaction()
        await User.create({"email": "tx_test@example.com", "name": "TX Test", "is_admin": False})
        user = await User.where("email", "tx_test@example.com").first()
        assert user is not None
        await conn.rollback()
        user_after = await User.where("email", "tx_test@example.com").first()
        assert user_after is None

    async def test_commit_persists_insert(self):
        conn = DB.connection("sqlite")
        await conn.begin_transaction()
        await User.create({"email": "commit_test@example.com", "name": "Commit Test", "is_admin": False})
        await conn.commit_transaction()
        user = await User.where("email", "commit_test@example.com").first()
        assert user is not None
