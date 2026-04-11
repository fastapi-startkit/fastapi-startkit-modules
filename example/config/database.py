from fastapi_startkit.masoniteorm.connections import ConnectionResolver

DATABASES = {
    "default": "sqlite",
    "sqlite": {
        "driver": "sqlite",
        "database": "test.db",
        "options": {"check_same_thread": False},
    }
}

DB = ConnectionResolver().set_connection_details(DATABASES)
