from dataclasses import dataclass, field
from typing import Any, Dict

from fastapi_startkit.environment import env
from fastapi_startkit.masoniteorm import SQLiteConfig


@dataclass
class DatabaseConfig:
    default: str = field(default_factory=lambda: env("DB_CONNECTION", "pgsql"))

    connections: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {
            "sqlite": SQLiteConfig(
                driver="sqlite",
                database=env("DB_DATABASE", "database.sqlite"),
                options=None,
            ),
        }
    )

    migrations: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {"table": "migrations", "path": "databases/migrations"}
    )
