from pathlib import Path

from fastapi_startkit import Application
from fastapi_startkit.logging import LogProvider
from fastapi_startkit.fastapi import FastAPIProvider

app: Application = Application(
    base_path=str(Path.cwd()), # This always gives path relative to the execution.
    providers=[
        LogProvider,
        FastAPIProvider,
    ]
)
