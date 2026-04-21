import os
from dataclasses import field, dataclass

@dataclass
class AppConfig:
    name: str = field(default_factory=lambda: os.getenv('APP_NAME', 'FastAPI starter kit'))
    env: str = field(default_factory=lambda: os.getenv('APP_ENV', 'development'))
    timezone: str = field(default_factory=lambda: os.getenv('APP_TIMEZONE', 'UTC'))
