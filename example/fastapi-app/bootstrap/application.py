from pathlib import Path

from fastapi_startkit.application import Application
from fastapi_startkit.logging.providers import LogProvider
from fastapi_startkit.fastapi.providers.fastapi_provider import FastAPIProvider

app: Application = Application(
    base_path=str(Path.cwd()), # This always gives path relative to the execution.
    providers=[
        LogProvider,
        FastAPIProvider,
    ]
)
