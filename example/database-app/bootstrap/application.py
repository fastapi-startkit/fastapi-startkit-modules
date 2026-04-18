from pathlib import Path

from fastapi_startkit.application import Application
from fastapi_startkit.logging.providers import LogProvider
from fastapi_startkit.masoniteorm.providers import DatabaseProvider
from providers.fastapi_provider import FastAPIServiceProvider
from app.commands.list_users_command import ListUsersCommand

app: Application = Application(
    base_path=str(Path().cwd()),
    providers=[
        LogProvider,
        DatabaseProvider,
        FastAPIServiceProvider,
    ]
)

app.add_commands([ListUsersCommand])
