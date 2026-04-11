import os
from fastapi_startkit.providers import Provider

from ..ChannelFactory import ChannelFactory
from ..logger import Logger
from ..factory import DriverFactory
from ..listeners import LoggerExceptionListener
from ..managers import LoggingManager


class LogProvider(Provider):
    def register(self):
        self.merge_config_from(self.config, 'logging')
        source = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config/logging.py"))
        self.merge_config_from(source, 'logging')

        self.app.bind('LogChannelFactory', ChannelFactory)
        self.app.bind('LogDriverFactory', DriverFactory)
        self.app.bind('LoggingManager', LoggingManager(ChannelFactory, DriverFactory))
        self.app.simple(LoggerExceptionListener)

    def boot(self):
        source = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config/logging.py"))
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
