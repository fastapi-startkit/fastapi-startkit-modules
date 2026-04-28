from pathlib import Path

from config.database import DatabaseConfig
from config.logging import LoggingConfig
from providers.console_provider import ConsoleProvider
from providers.fastapi_provider import FastAPIServiceProvider

from config.app import AppConfig

print("Loading Application class...")
from fastapi_startkit.application import Application
from fastapi_startkit.exceptions import ExceptionHandler
from fastapi_startkit.logging.providers import LogProvider
from fastapi_startkit.masoniteorm.providers import DatabaseProvider


class AppExceptionHandler(ExceptionHandler):
    def register(self):
        pass

print("Creating app instance...")
app: Application[AppConfig] = Application(
    base_path=str(Path().cwd()),
    config=AppConfig,
    providers=[
        (LogProvider, LoggingConfig),
        ConsoleProvider,
        (DatabaseProvider, DatabaseConfig),
        FastAPIServiceProvider,
    ],
    exception_handler=AppExceptionHandler,
)
