from fastapi_startkit.masoniteorm.connections.factory import ConnectionFactory
from fastapi_startkit.masoniteorm.connections.manager import DatabaseManager
from fastapi_startkit.masoniteorm.models.model import Model
from fastapi_startkit.masoniteorm.models.registry import Registry

DB = DatabaseManager(
    ConnectionFactory(),
    {
        "default": "sqlite",
        "connections": {
            "sqlite": {
                "driver": "sqlite",
                "url": "sqlite+aiosqlite:///masonite.sqlite3",
            },
            "dev": {
                "driver": "sqlite",
                "url": "sqlite+aiosqlite:///masonite_dev.sqlite3",
            },
        },
    },
)

Model.db_manager = DB
