from pathlib import Path

from fastapi_startkit import Application

app: Application = Application(
    base_path=Path(__file__).parent.parent,
)
