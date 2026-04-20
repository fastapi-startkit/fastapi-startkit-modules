from fastapi_startkit.providers import Provider

class ConsoleProvider(Provider):
    def register(self) -> None:
        from config.database import DATABASES

        self.merge_config_from(, 'database')
