from pathlib import Path

from fastapi_startkit.application import Application
from fastapi_startkit.logging.providers import LogProvider
# from providers.console import ConsoleServiceProvider

providers = [
    LogProvider,
    # ConsoleServiceProvider
]

app: Application = Application(
    base_path=str(Path().cwd()),
    providers=providers
)

#
from commands.example_command import ExampleCommand
app.add_commands([
    ExampleCommand
])
