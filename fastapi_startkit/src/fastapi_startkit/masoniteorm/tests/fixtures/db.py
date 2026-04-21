from fastapi_startkit.orm.connections.factory import ConnectionFactory
from fastapi_startkit.orm.connections.manager import DatabaseManager
from fastapi_startkit.orm.models.model import Model

DB = DatabaseManager(ConnectionFactory(), {
    "default": "sqlite",
    "sqlite": {
        "driver": "sqlite",
        "url": "sqlite+aiosqlite:///masonite.sqlite3",
    }
})

Model.db_manager = DB
