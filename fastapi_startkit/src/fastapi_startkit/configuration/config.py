from typing import Any


class Config:
    @staticmethod
    def instance():
        from fastapi_startkit.application import app

        return app().make("config")

    @staticmethod
    def get(path: str, default: Any = None) -> Any:
        return Config.instance().get(path, default)

    @staticmethod
    def set(path: str, value: Any) -> None:
        Config.instance().set(path, value)

    @staticmethod
    def has(path: str) -> bool:
        return Config.instance().has(path)

    @staticmethod
    def all() -> dict:
        return Config.instance().all()
