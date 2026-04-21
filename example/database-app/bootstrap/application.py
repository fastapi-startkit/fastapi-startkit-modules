from pathlib import Path

from config.database import DatabaseConfig
from dumpdie import dd
from providers.console_provider import ConsoleProvider
from providers.fastapi_provider import FastAPIServiceProvider

from config.app import AppConfig
from fastapi_startkit.application import Application
from fastapi_startkit.logging.providers import LogProvider
from fastapi_startkit.masoniteorm.providers import DatabaseProvider
from config.logging import LoggingConfig

app: Application[AppConfig] = Application(
    base_path=str(Path().cwd()),
    config=AppConfig,
    providers=[
        (LogProvider, LoggingConfig),
        ConsoleProvider,
        (DatabaseProvider, DatabaseConfig),
        FastAPIServiceProvider,
    ],
)
