from fastapi_startkit.facades import Config

from ..channels.BaseChannel import BaseChannel
from ..factory import DriverFactory


class TerminalChannel(BaseChannel):
    def __init__(self, driver=None, path=None):
        self.max_level = Config.get("logging.channels.terminal.level", "debug")
        self.driver = DriverFactory.make(driver or Config.get("logging.channels.terminal.driver"))(
            path=path, max_level=self.max_level
        )
