import asyncio

from dumpdie import dd

from fastapi_startkit.carbon import Carbon
from fastapi_startkit.orm.connections.factory import ConnectionFactory
from fastapi_startkit.masoniteorm.models.fields import DateTimeField
from fastapi_startkit.orm.connections.manager import DatabaseManager
from fastapi_startkit.orm.models.model import Model

DB = DatabaseManager(ConnectionFactory(), {
    "default": "sqlite",
    "sqlite": {
        "driver": "sqlite",
        "url": "sqlite+aiosqlite:///masonite.sqlite3",
    }
})

# Set the db_manager for model
Model.db_manager = DB


class User(Model):
    id: int
    name: str
    email: str

    email_verified_at: Carbon = DateTimeField(fmt="%Y-%m-%d %H:%M:%S", tz="UTC")


async def main():
    user = User(name="Alex", email='alex@gmail.com', email_verified_at="2026-10-01 12:12:12")
    print(user.name)
    print(user.email)
    print(user.created_at)
    dd(user.email_verified_at.format("YYYY-MM-DD HH:mm:ss"))


if __name__ == "__main__":
    asyncio.run(main())
