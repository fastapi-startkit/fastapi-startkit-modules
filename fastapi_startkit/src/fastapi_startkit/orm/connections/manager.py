from fastapi_startkit.orm.connections.factory import ConnectionFactory


class DatabaseManager:
    def __init__(self, factory: ConnectionFactory, config: dict):
        self.factory = factory
        self.config = config
        self.connections = {}

    def connection(self, name: str | None):
        name = self.get_default_connection_name(name)
        assert name is not None
        config = self.config[name]
        if name not in self.connections:
            self.connections[name] = self.factory.make(config, name)

        return self.connections[name]

    def disconnect(self):
        pass

    def reconnect(self):
        pass

    def get_default_connection_name(self, name: str | None) -> str:
        if name is None or name == "default":
            return self.config.get("default", "default")
        return name
