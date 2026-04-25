from typing import TypeVar, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi_startkit.config import AppConfig

TConfig = TypeVar("TConfig", bound="AppConfig")


def Config(cls: Type[TConfig] | None = None) -> TConfig:
    from fastapi_startkit.application import app

    return app().config  # type: ignore[return-value]
