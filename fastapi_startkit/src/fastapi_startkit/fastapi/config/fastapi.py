import dataclasses

from fastapi_startkit.environment import env


@dataclasses.dataclass
class FastAPIConfig:
    """Server configuration for the uvicorn/FastAPI serve command.

    All fields can be overridden via environment variables or by publishing a
    ``config/fastapi.py`` file in the application root.
    """

    host: str = dataclasses.field(default_factory=lambda: env("APP_HOST", "127.0.0.1"))
    port: int = dataclasses.field(default_factory=lambda: env("APP_PORT", 8000))
    reload: bool = dataclasses.field(default_factory=lambda: env("APP_RELOAD", True))
    reload_dirs: list = dataclasses.field(
        default_factory=lambda: []
    )
    reload_excludes: list = dataclasses.field(
        default_factory=lambda: ["*.log", "tests/*"]
    )
