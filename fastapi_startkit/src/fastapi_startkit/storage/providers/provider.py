from pathlib import Path
from ...providers import Provider
from ..storage import StorageManager
from ...configuration import config
from ..drivers import LocalDriver, S3Driver
from ..config import StorageConfig


class StorageProvider(Provider):
    def __init__(self, application):
        self.application = application

    def register(self):
        config_data = self.resolve_config(StorageConfig)
        self.merge_config_from(config_data, "storage")
        
        storage = StorageManager(self.application, config("storage"))
        storage.add_driver("local", LocalDriver(self.application))
        storage.add_driver("s3", S3Driver(self.application))
        self.application.bind("storage", storage)

    def boot(self):
        self.publishes(
            {
                Path(__file__)
                .resolve()
                .parent.parent.joinpath("config.py"): "config/storage.py"
            }
        )