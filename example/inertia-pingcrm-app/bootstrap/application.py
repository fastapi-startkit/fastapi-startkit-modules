from pathlib import Path

from config.database import DatabaseConfig
from fastapi_startkit import Application
from fastapi_startkit.logging import LogProvider
from fastapi_startkit.vite import ViteProvider
from fastapi_startkit.inertia import InertiaProvider
from fastapi_startkit.masoniteorm import DatabaseProvider

from providers.fastapi_provider import FastAPIProvider

app: Application = Application(
    base_path=str(Path.cwd()),
    providers=[
        LogProvider,
        (DatabaseProvider, DatabaseConfig),
        FastAPIProvider,
        ViteProvider,
        InertiaProvider,
    ],
)
