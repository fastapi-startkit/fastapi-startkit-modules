import unittest

from ...fixtures.model import User
from ...fixtures.db import DB


class TestSQLiteQueryBuilder(unittest.TestCase):
    def test_where_generates_sql(self):
        sql = User.query().where("name", "Joe").to_sql()
        self.assertIn("WHERE", sql)
        self.assertIn("name", sql)

    def test_where_with_operator(self):
        sql = User.query().where("age", ">", 20).to_sql()
        self.assertIn(">", sql)

    def test_select_columns(self):
        sql = User.query().select("name", "email").to_sql()
        self.assertIn("name", sql)
        self.assertIn("email", sql)

    def test_limit(self):
        sql = User.query().limit(5).to_sql()
        self.assertIn("LIMIT 5", sql)

    def test_offset(self):
        sql = User.query().limit(10).offset(5).to_sql()
        self.assertIn("OFFSET 5", sql)

    def test_order_by_asc(self):
        sql = User.query().order_by("email", "asc").to_sql()
        self.assertIn("ORDER BY", sql)
        self.assertIn("ASC", sql)

    def test_order_by_desc(self):
        sql = User.query().order_by("email", "desc").to_sql()
        self.assertIn("DESC", sql)

    def test_where_null(self):
        sql = User.query().where_null("name").to_sql()
        self.assertIn("IS NULL", sql)

    def test_where_not_null(self):
        sql = User.query().where_not_null("name").to_sql()
        self.assertIn("IS NOT NULL", sql)

    def test_where_in(self):
        sql = User.query().where_in("id", [1, 2, 3]).to_sql()
        self.assertIn("IN", sql)

    def test_where_not_in(self):
        sql = User.query().where_not_in("id", [1, 2, 3]).to_sql()
        self.assertIn("NOT IN", sql)

    def test_between(self):
        sql = User.query().between("id", 2, 5).to_sql()
        self.assertIn("BETWEEN", sql)

    def test_not_between(self):
        sql = User.query().not_between("id", 2, 5).to_sql()
        self.assertIn("NOT BETWEEN", sql)

    def test_join(self):
        sql = User.query().join("profiles", "users.id", "=", "profiles.user_id").to_sql()
        self.assertIn("JOIN", sql)
        self.assertIn("profiles", sql)

    def test_left_join(self):
        sql = User.query().left_join("profiles", "users.id", "=", "profiles.user_id").to_sql()
        self.assertIn("LEFT JOIN", sql)

    def test_or_where(self):
        sql = User.query().where("age", "20").or_where("age", "<", 20).to_sql()
        self.assertIn("OR", sql)

    def test_where_column(self):
        sql = User.query().where_column("name", "username").to_sql()
        self.assertIn("name", sql)

    def test_when_true(self):
        sql = User.query().when(True, lambda q: q.where("is_admin", 1)).to_sql()
        self.assertIn("is_admin", sql)

    def test_when_false(self):
        sql = User.query().when(False, lambda q: q.where("is_admin", 1)).to_sql()
        self.assertNotIn("is_admin", sql)
