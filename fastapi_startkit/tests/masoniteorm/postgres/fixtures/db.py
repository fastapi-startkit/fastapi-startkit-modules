from fastapi_startkit.masoniteorm.connections.factory import ConnectionFactory
from fastapi_startkit.masoniteorm.connections.manager import DatabaseManager

URL = "postgresql+asyncpg://app:secret@localhost:5432/database_app_test"

DB = DatabaseManager(
    ConnectionFactory(),
    {
        "default": "postgres",
        "connections": {
            "postgres": {
                "driver": "postgres",
                "url": URL,
                "database": "database_app_test",
            },
            "dev": {
                "driver": "postgres",
                "url": URL,
                "database": "database_app_test",
            },
        },
    },
)

schema = DB.get_schema_builder()
