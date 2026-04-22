from fastapi_startkit.environment.environment import env

# Flat config for DatabaseManager compatibility
default = env("DB_CONNECTION", "pgsql")

pgsql = {
    "driver": "postgres",
    "host": env("DB_HOST", "127.0.0.1"),
    "port": env("DB_PORT", "5432"),
    "database": env("DB_DATABASE", "fastapi"),
    "username": env("DB_USERNAME", "postgres"),
    "password": env("DB_PASSWORD", ""),
}

postgres = {
    "driver": "postgres",
    "host": env("DB_HOST", "127.0.0.1"),
    "port": env("DB_PORT", "5432"),
    "database": env("DB_DATABASE", "fastapi"),
    "username": env("DB_USERNAME", "postgres"),
    "password": env("DB_PASSWORD", ""),
}

sqlite = {
    "driver": "sqlite",
    "database": env("DB_DATABASE", "database.sqlite"),
}
