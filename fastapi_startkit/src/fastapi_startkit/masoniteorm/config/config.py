from dataclasses import dataclass
from typing import Any, Dict, Optional

from fastapi_startkit.environment.environment import env


@dataclass
class SQLiteConfig:
    driver: str = "sqlite"
    url: Optional[str] = env("DB_URL", None)
    database: str = env("DB_DATABASE", "database.sqlite")
    options: Optional[Dict[str, Any]] = None


@dataclass
class MySQLConfig:
    driver: str = "mysql"
    url: Optional[str] = env("DB_URL", None)
    host: str = env("DB_HOST", "127.0.0.1")
    port: int = env("DB_PORT", 3306)
    database: str = env("DB_DATABASE", "inertia")
    username: str = env("DB_USERNAME", "root")
    password: str = env("DB_PASSWORD", "")
    unix_socket: str = env("DB_SOCKET", "")
    charset: str = env("DB_CHARSET", "utf8mb4")
    collation: str = env("DB_COLLATION", "utf8mb4_unicode_ci")
    options: Optional[Dict[str, Any]] = None


@dataclass
class PostgresConfig:
    driver: str = "postgres"
    url: Optional[str] = env("DB_URL", None)
    host: str = env("DB_HOST", "127.0.0.1")
    port: int = env("DB_PORT", 5432)
    database: str = env("DB_DATABASE", "inertia")
    username: str = env("DB_USERNAME", "postgres")
    password: str = env("DB_PASSWORD", "")
    charset: str = env("DB_CHARSET", "utf8")
    sslmode: str = env("DB_SSLMODE", "prefer")
    options: Optional[Dict[str, Any]] = None
