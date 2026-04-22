import dataclasses

from fastapi_startkit.environment.environment import env


@dataclasses.dataclass
class SingleChannel:
    driver: str = 'single'
    level: str = 'debug'
    path: str = 'storage/logs/single.log'


@dataclasses.dataclass
class StackChannel:
    driver: str = 'stack'
    channels: list = dataclasses.field(default_factory=lambda: ['daily', 'terminal'])


@dataclasses.dataclass
class DailyChannel:
    driver: str = 'daily'
    level: str = 'debug'
    path: str = 'storage/logs'


@dataclasses.dataclass
class TerminalChannel:
    driver: str = 'terminal'
    level: str = 'info'


@dataclasses.dataclass
class SlackChannel:
    driver: str = 'slack'
    channel: str = '#bot'
    emoji: str = ':warning:'
    username: str = 'Logging Bot'
    token: str = None
    level: str = 'debug'


@dataclasses.dataclass
class SyslogChannel:
    driver: str = 'syslog'
    path: str = '/var/run/syslog'
    level: str = 'debug'
