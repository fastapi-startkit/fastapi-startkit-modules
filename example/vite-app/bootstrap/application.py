from pathlib import Path

from fastapi_startkit.application import Application
from fastapi_startkit.logging.providers import LogProvider
from fastapi_startkit.vite import ViteProvider

from providers.fastapi_provider import FastAPIProvider

app: Application = Application(
    base_path=str(Path.cwd()),
    providers=[
        LogProvider,
        FastAPIProvider,
        (ViteProvider, {
            "build_directory": "build",
            # "asset_url": "https://cdn.example.com",  # optional CDN prefix
        }),
    ],
)
