from pathlib import Path

from fastapi_startkit.application import Application
from fastapi_startkit.logging.providers import LogProvider
from fastapi_startkit.vite import ViteProvider
from fastapi_startkit.inertia import InertiaProvider
from fastapi_startkit.masoniteorm.providers import DatabaseProvider

from providers.fastapi_provider import FastAPIProvider

app: Application = Application(
    base_path=str(Path.cwd()),
    providers=[
        LogProvider,
        DatabaseProvider,
        FastAPIProvider,
        (ViteProvider, {
            "build_directory": "build",
            # "asset_url": "https://cdn.example.com",  # optional CDN prefix
        }),
        InertiaProvider,
    ],
)
