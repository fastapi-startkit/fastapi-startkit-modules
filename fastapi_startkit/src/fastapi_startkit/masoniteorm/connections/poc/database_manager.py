import asyncio

from dumpdie import dd
from pendulum import now

from fastapi_startkit.carbon import Carbon
from fastapi_startkit.masoniteorm.connections.poc.attribute import Attribute
from fastapi_startkit.masoniteorm.connections.poc.connection_factory import ConnectionFactory
from fastapi_startkit.masoniteorm.connections.poc.relationship import Relationship
from fastapi_startkit.masoniteorm.models.fields import CreatedAtField, UpdatedAtField, DateTimeField
from fastapi_startkit.masoniteorm.observers import ObservesEvents


class DatabaseManager:
    def __init__(self, factory: ConnectionFactory, config: dict):
        self.factory = factory
        self.config = config
        self.connections = {}

    def connection(self, name: str | None):
        name = self.get_default_connection_name(name)
        assert name is not None
        config = self.config[name]
        if name not in self.connections:
            self.connections[name] = self.factory.make(config, name)

        return self.connections[name]

    def disconnect(self):
        pass

    def reconnect(self):
        pass

    def get_default_connection_name(self, name: str | None) -> str:
        if name is None or name == "default":
            return self.config.get("default", "default")
        return name


class Model(Attribute, Relationship, ObservesEvents):
    db_manager: 'DatabaseManager' = None

    __observers__ = {}
    __has_events__ = True

    created_at: Carbon = CreatedAtField(fmt="%Y-%m-%d %H:%M:%S", tz="UTC")
    updated_at: Carbon = UpdatedAtField(fmt="%Y-%m-%d %H:%M:%S", tz="UTC")

    def __init__(self, attributes: dict = None, **kwargs):
        super().__init__(attributes, **kwargs)
        self.connection = 'default'
        self._global_scopes = {}
        self.__with__ = {}

    def new_query(self):
        return self.db_manager.connection(self.connection).query().set_model(self)

    def __getattr__(self, attribute):
        return self.get_attribute(attribute)

    @classmethod
    def query(cls):
        return cls().new_query()


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
