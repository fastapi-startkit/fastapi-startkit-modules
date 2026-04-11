from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..container import Container

class Provider:
    def __init__(self, application, config: dict = None):
        self.app = application
        self.config = config or {}

    def register(self) -> None:
        pass

    def boot(self) -> None:
        pass

    def merge_config_from(self, source: str | dict, key: str) -> None:
        self.app.make('config').merge_with(key, source)

    def publishes(self, resources: dict, tag: str = None) -> None:
        self.app.published_resources.update(resources)

    def commands(self, commands: list) -> None:
        self.app.add_commands(commands)
