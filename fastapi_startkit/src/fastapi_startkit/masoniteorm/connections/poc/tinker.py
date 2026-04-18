import asyncio
import os

from connection import Connection
from connection_factory import ConnectionFactory

config = {
    "default": "sqlite",
    "connections": {
        "sqlite": {
            "driver": "sqlite",
            "url": os.getenv("DB_URL", "sqlite+aiosqlite:///:memory:"),
        },
        "mysql": {
            "driver": "mysql",
            "host": os.getenv("DB_HOST", "127.0.0.1"),
            "port": os.getenv("DB_PORT", "3306"),
            "database": os.getenv("DB_DATABASE", "app"),
            "username": os.getenv("DB_USERNAME", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
        },
        "postgres": {
            "driver": "postgres",
            "host": os.getenv("DB_HOST", "127.0.0.1"),
            "port": os.getenv("DB_PORT", "5432"),
            "database": os.getenv("DB_DATABASE", "app"),
            "username": os.getenv("DB_USERNAME", "postgres"),
            "password": os.getenv("DB_PASSWORD", ""),
        },
    }
}

class Builder:
    def __init__(self):
        self.connection = Connection()

    def create(self, creates: dict):
        pass

class Model:
    builder = None
    resolver = None

    def __init__(self):
        self.builder = Builder()

    def create(self, creates: dict):

        from dumpdie import dd
        dd(self.resolver)
        model = self.builder.create(creates)
        # set the primary keys
        self.hydrate()

        return self

    def hydrate(self):
        pass

class User(Model):
    pass

async def main():
    ConnectionFactory.configure(config)

    db = Connection.query()

    await db.statement("""
        CREATE TABLE users (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age  INTEGER
        )
    """)

    await Connection.query().insert(
        "INSERT INTO users (name, age) VALUES (:name, :age)",
        {"name": "Alice", "age": 30},
    )
    await Connection.query().insert(
        "INSERT INTO users (name, age) VALUES (:name, :age)",
        {"name": "Bob", "age": 25},
    )

    # commit path
    conn = Connection.query()
    await conn.begin_transaction()
    await conn.update("UPDATE users SET age = :age WHERE name = :name", {"age": 31, "name": "Alice"})
    await conn.delete("DELETE FROM users WHERE name = :name", {"name": "Bob"})
    await conn.commit_transaction()

    print("after commit  :", await db.select("SELECT * FROM users"))

    # rollback path
    conn2 = Connection.query()
    await conn2.begin_transaction()
    await conn2.update("UPDATE users SET age = :age WHERE name = :name", {"age": 99, "name": "Alice"})
    await conn2.rollback()

    print("after rollback:", await db.select("SELECT * FROM users"))


Model.resolver = ConnectionFactory.configure(config)
User().create({})
# asyncio.run(main())

# # TO consider:
# 1. Builder
# 2. Caster
# 3. Observer
