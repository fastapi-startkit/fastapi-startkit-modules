import os

from fastapi_startkit.providers import Provider
from ..ChannelFactory import ChannelFactory
from ..config.logging import LoggingConfig
from ..factory import DriverFactory
from ..logger import Logger
from ..managers import LoggingManager


class LogProvider(Provider):
    provider_key = 'logging'

    def register(self):
        config = self.resolve_config(LoggingConfig)
        self.merge_config_from(config, self.provider_key)

        self.app.bind('LogChannelFactory', ChannelFactory)
        self.app.bind('LogDriverFactory', DriverFactory)
        self.app.bind('LoggingManager', LoggingManager(ChannelFactory, DriverFactory))

    def boot(self):
        source = os.path.abspath(str(os.path.join(str(os.path.dirname(__file__)), "../config/logging.py")))
        self.publishes({
            source: 'config/logging.py'
        })
        config = self.app.make('config')
        if not config.get('logging.default'):
            return
        logger = self.app.make('LoggingManager')
        channel = logger.channel(config.get('logging.default'))

        self.app.bind('logger', channel)
        self.app.swap(Logger, channel)
