from pathlib import Path

from fastapi_startkit.application import Application
from fastapi_startkit.logging.providers import LogProvider
from fastapi_startkit.masoniteorm.providers import DatabaseProvider
from providers.fastapi_provider import FastAPIServiceProvider

app: Application = Application(
    base_path=str(Path().cwd()),
    providers=[
        LogProvider,
        DatabaseProvider,
        FastAPIServiceProvider,
    ]
)
