from dataclasses import field

from pydantic.dataclasses import dataclass

from fastapi_startkit.environment.environment import env


@dataclass
class DatabaseConnection:
    driver: str | None = None
    host: str | None = None
    database: str | None = None
    username: str | None = None
    password: str | None = None
    port: int | None = None
    prefix: str | None = None
    options: dict = field(default_factory=dict)

@dataclass
class DatabaseConfig:
    default: str = "postgres"

    connections: dict[str, DatabaseConnection] = field(default_factory=lambda: {
        "sqlite": DatabaseConnection(
            driver="sqlite",
            database=env("DB_DATABASE", "database.sqlite"),
        ),
        "mysql": DatabaseConnection(
            driver="mysql",
            host=env("DB_HOST", "127.0.0.1"),
            database=env("DB_DATABASE", "laravel"),
            username=env("DB_USERNAME", "root"),
            password=env("DB_PASSWORD", ""),
            port=env("DB_PORT", "3306"),
            options={
                "charset": "utf8mb4"
            }
        ),
    })

    migration_path: str =field(default_factory=lambda: env("MIGRATION_PATH", "database/migrations"))
