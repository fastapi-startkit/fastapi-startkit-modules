import asyncio

from dumpdie import dd

from fastapi_startkit.carbon import Carbon
from fastapi_startkit.orm.connections.factory import ConnectionFactory
from fastapi_startkit.masoniteorm.models.fields import DateTimeField
from fastapi_startkit.orm.connections.manager import DatabaseManager
from fastapi_startkit.orm.models import Model
from fastapi_startkit.orm.tests.fixtures.factory import UserFactory

DB = DatabaseManager(ConnectionFactory(), {
    "default": "sqlite",
    "sqlite": {
        "driver": "sqlite",
        "url": "sqlite+aiosqlite:///masonite.sqlite3",
    }
})

# Set the db_manager for model
Model.db_manager = DB
schema = DB.get_schema_builder()



class User(Model):
    id: int
    name: str
    email: str

    email_verified_at: Carbon = DateTimeField(fmt="%Y-%m-%d %H:%M:%S", tz="UTC")


async def main():
    await schema.drop_table_if_exists('users')
    async with await schema.on('default').create("users") as table:
        table.id()
        table.string("name")
        table.string("email").unique()
        table.timestamp('email_verified_at').nullable()
        table.timestamps()

    user = await UserFactory.create()
    dd(user)

    user = User(name="Alex", email='alex@gmail.com', email_verified_at="2026-10-01 12:12:12")
    await user.save()

    user.name = "Ram"
    await user.save()

    users = await User.get()
    dd(users)


if __name__ == "__main__":
    asyncio.run(main())

