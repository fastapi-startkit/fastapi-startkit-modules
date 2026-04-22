import dataclasses
from typing import TYPE_CHECKING

from fastapi_startkit.helper.string import Str

if TYPE_CHECKING:
    from ..application import Application


class Provider:
    provider_key: str = None

    def __init__(self, application: 'Application', config: dict = None):
        self.app: 'Application' = application
        self.config = config or {}

        if self.provider_key is None:
            self.provider_key = str(
                Str.of(self.__class__.__name__)
                .trim('ServiceProvider')
                .trim('Provider')
                .slugify()
            )

    def register(self) -> None:
        pass

    def boot(self) -> None:
        pass

    def resolve_config(self, default)->dict:
        if isinstance(self.config, dict):
            user_config = self.config
        elif dataclasses.is_dataclass(self.config):
            instance = self.config() if isinstance(self.config, type) else self.config
            # pydantic dataclasses expose model_dump(); stdlib dataclasses use asdict()
            user_config = instance.model_dump() if hasattr(instance, 'model_dump') else dataclasses.asdict(instance)
        else:
            raise TypeError(f"{self.__class__.__name__} config must be a dict or a dataclass, got {type(self.config).__name__}")

        return {**dataclasses.asdict(default()), **user_config}

    def merge_config_from(self, source: str | dict, provider_key: str) -> None:
        self.app.make('config').merge_with(provider_key, source)

    def publishes(self, resources: dict, tag: str = None) -> None:
        self.app.published_resources.setdefault(self.provider_key, {}).update(resources)

    def commands(self, commands: list) -> None:
        self.app.add_commands(commands)
