from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..container import Container

class Provider:
    def __init__(self, application, config: dict = None):
        self.application = application
        self.config = config or {}

    def register(self) -> None:
        pass

    def boot(self) -> None:
        pass

    def merge_config_from(self, source: str | dict, key: str) -> None:
        self.application.make('config').merge_with(key, source)

    def publishes(self, resources: dict, tag: str = None) -> None:
        self.application.published_resources.update(resources)

    def commands(self, commands: list) -> None:
        """
        Register the given commands with the application.
        """
        cli = self.application.cli
        for command in commands:
            # If it's a class with a register method (common in some patterns)
            if hasattr(command, 'register'):
                command.register(cli)
            # If it's already a Typer instance or a callable that Typer can handle
            else:
                try:
                    from typer import Typer
                    if isinstance(command, Typer):
                        cli.add_typer(command)
                    else:
                        # Fallback: assume it's a function we want to register as a command
                        cli.command()(command)
                except ImportError:
                    pass
