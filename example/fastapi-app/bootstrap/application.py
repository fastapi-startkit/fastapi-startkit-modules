from pathlib import Path

from fastapi_startkit.application import Application
from fastapi_startkit.logging.providers import LogProvider
from providers.fastapi_provider import FastAPIServiceProvider

app: Application = Application(
    base_path=str(Path.cwd()), # This always gives path relative to the execution.
    providers=[
        LogProvider,
        FastAPIServiceProvider,
    ]
)
