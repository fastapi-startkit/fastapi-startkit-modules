import os

DATABASES = {
    "default": "postgres",
    "postgres": {
        "driver": "postgres",
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "database": os.getenv("DB_DATABASE", "local"),
        "user": os.getenv("DB_USERNAME", "local"),
        "password": os.getenv("DB_PASSWORD", "secret"),
        "port": os.getenv("DB_PORT", "5432"),
        "prefix": "",
        "options": {
            "min_size": 1,
            "max_size": 10,
        },
    },
}
