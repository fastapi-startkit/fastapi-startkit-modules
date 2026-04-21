from pathlib import Path

from config.database import DatabaseConfig
from providers.console_provider import ConsoleProvider
from providers.fastapi_provider import FastAPIServiceProvider

from config.app import AppConfig
from fastapi_startkit.application import Application
from fastapi_startkit.logging.providers import LogProvider
from fastapi_startkit.masoniteorm.providers import DatabaseProvider

app: Application[AppConfig] = Application(
    base_path=str(Path().cwd()),
    config=AppConfig,
    providers=[
        LogProvider,
        ConsoleProvider,
        (DatabaseProvider, DatabaseConfig),
        FastAPIServiceProvider,
    ],
)
