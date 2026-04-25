from fastapi_startkit.commands.publish_command import PublishCommand
from fastapi_startkit.providers import Provider


class AppProvider(Provider):
    def register(self) -> None:
        pass

    def boot(self) -> None:
        self.commands([PublishCommand])
