from dataclasses import dataclass, field
from typing import Dict, Any
from fastapi_startkit.environment.environment import env

@dataclass
class DatabaseConfig:
    default: str = field(default_factory=lambda: env("DB_CONNECTION", "pgsql"))
    
    pgsql: Dict[str, Any] = field(default_factory=lambda: {
        "driver": "postgres",
        "host": env("DB_HOST", "127.0.0.1"),
        "port": env("DB_PORT", "5432"),
        "database": env("DB_DATABASE", "inertia"),
        "username": env("DB_USERNAME", "postgres"),
        "password": env("DB_PASSWORD", ""),
    })
    
    postgres: Dict[str, Any] = field(default_factory=lambda: {
        "driver": "postgres",
        "host": env("DB_HOST", "127.0.0.1"),
        "port": env("DB_PORT", "5432"),
        "database": env("DB_DATABASE", "inertia"),
        "username": env("DB_USERNAME", "postgres"),
        "password": env("DB_PASSWORD", ""),
    })
    
    sqlite: Dict[str, Any] = field(default_factory=lambda: {
        "driver": "sqlite",
        "database": env("DB_DATABASE", "database.sqlite"),
    })
