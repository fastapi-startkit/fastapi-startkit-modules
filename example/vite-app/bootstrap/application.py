from pathlib import Path

from config.vite import ViteConfig
from fastapi_startkit.application import Application
from fastapi_startkit.logging import LogProvider
from fastapi_startkit.vite import ViteProvider

from providers.fastapi_provider import FastAPIProvider

app: Application = Application(
    base_path=str(Path.cwd()),
    providers=[
        LogProvider,
        FastAPIProvider,
        (ViteProvider, ViteConfig),
    ],
)
