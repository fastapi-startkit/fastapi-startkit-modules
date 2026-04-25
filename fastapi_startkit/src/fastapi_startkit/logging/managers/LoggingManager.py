class LoggingManager:
    def __init__(self, channel_factory=None, driver_factory=None):
        self.channel_factory = channel_factory
        self.driver_factory = driver_factory
        self.configure_python_logging()

    def channel(self, channel):
        return self.channel_factory.make(channel)()

    @classmethod
    def configure_python_logging(cls):
        from ..handler import LoggingHandler

        LoggingHandler.install()
