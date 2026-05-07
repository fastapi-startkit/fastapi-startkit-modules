from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..foundation import Application


class StorageManager:
    """File storage manager handling managing files with different drivers."""

    def __init__(self, application: "Application", store_config: dict = None):
        self.application = application
        self.drivers = {}
        self.store_config = store_config or {}
        self.options = {}

    def add_driver(self, name: str, driver: Any):
        self.drivers.update({name: driver})

    def set_configuration(self, config: dict) -> "StorageManager":
        self.store_config = config
        return self

    def get_driver(self, name: str = None) -> Any:
        if name is None:
            name = self.store_config.get("default")
        
        driver_name = self.get_config_options(name).get("driver")
        return self.drivers[driver_name]

    def get_config_options(self, name: str = None) -> dict:
        disks = self.store_config.get("disks", {})
        if name is None or name == "default":
            name = self.store_config.get("default")

        return disks.get(name, {})

    def disk(self, name: str = "default") -> Any:
        """Get the file manager instance for the given disk name."""
        if name == "default":
            name = self.store_config.get("default")

        store_config = self.get_config_options(name)
        driver = self.get_driver(name)
        return driver.set_options(store_config)

    def fake(self, name: str = "default") -> Any:
        """Replace the given disk with a fake local disk for testing."""
        if name == "default":
            name = self.store_config.get("default", "local")

        from .drivers import LocalDriver
        import tempfile

        # Use a temporary directory for the fake storage
        temp_dir = tempfile.mkdtemp(prefix=f"storage_fake_{name}_")
        
        fake_driver = LocalDriver(self.application)
        fake_driver.set_options({"root": temp_dir})
        
        # Replace the driver in the manager
        self.drivers[name] = fake_driver
        return fake_driver

    def put(self, *args, **kwargs):
        return self.disk().put(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.disk().get(*args, **kwargs)

    def exists(self, *args, **kwargs):
        return self.disk().exists(*args, **kwargs)

    def missing(self, *args, **kwargs):
        return self.disk().missing(*args, **kwargs)

    def stream(self, *args, **kwargs):
        return self.disk().stream(*args, **kwargs)

    def copy(self, *args, **kwargs):
        return self.disk().copy(*args, **kwargs)

    def move(self, *args, **kwargs):
        return self.disk().move(*args, **kwargs)

    def prepend(self, *args, **kwargs):
        return self.disk().prepend(*args, **kwargs)

    def append(self, *args, **kwargs):
        return self.disk().append(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.disk().delete(*args, **kwargs)

    def store(self, *args, **kwargs):
        return self.disk().store(*args, **kwargs)

    def download(self, *args, **kwargs):
        return self.disk().download(*args, **kwargs)

    def url(self, *args, **kwargs):
        return self.disk().url(*args, **kwargs)


class Storage:
    instance = None

    def __init__(self):
        from fastapi_startkit.application import app
        self.app = app()
        self.storage: StorageManager = self.app.make("storage")

    @classmethod
    def init(cls) -> StorageManager:
        if cls.instance:
            return cls.instance.storage
        cls.instance = Storage()
        return cls.instance.storage

    @classmethod
    def disk(cls, name="default"):
        return cls.init().disk(name)

    @classmethod
    def fake(cls, name="default"):
        return cls.init().fake(name)

    @classmethod
    def put(cls, *args, **kwargs):
        return cls.init().put(*args, **kwargs)

    @classmethod
    def get(cls, *args, **kwargs):
        return cls.init().get(*args, **kwargs)

    @classmethod
    def exists(cls, *args, **kwargs):
        return cls.init().exists(*args, **kwargs)

    @classmethod
    def missing(cls, *args, **kwargs):
        return cls.init().missing(*args, **kwargs)

    @classmethod
    def stream(cls, *args, **kwargs):
        return cls.init().stream(*args, **kwargs)

    @classmethod
    def copy(cls, *args, **kwargs):
        return cls.init().copy(*args, **kwargs)

    @classmethod
    def move(cls, *args, **kwargs):
        return cls.init().move(*args, **kwargs)

    @classmethod
    def prepend(cls, *args, **kwargs):
        return cls.init().prepend(*args, **kwargs)

    @classmethod
    def append(cls, *args, **kwargs):
        return cls.init().append(*args, **kwargs)

    @classmethod
    def delete(cls, *args, **kwargs):
        return cls.init().delete(*args, **kwargs)

    @classmethod
    def store(cls, *args, **kwargs):
        return cls.init().store(*args, **kwargs)

    @classmethod
    def download(cls, *args, **kwargs):
        return cls.init().download(*args, **kwargs)

    @classmethod
    def url(cls, *args, **kwargs):
        return cls.init().url(*args, **kwargs)