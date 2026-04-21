import dataclasses
from fastapi_startkit.environment.environment import env
from fastapi_startkit.logging.config import SingleChannel, StackChannel, DailyChannel, TerminalChannel, SlackChannel, SyslogChannel


@dataclasses.dataclass
class LoggingConfig:
    default: str = dataclasses.field(default_factory=lambda: env('LOG_CHANNEL', 'stack'))

    channels: dict = dataclasses.field(default_factory=lambda: {
        'single': SingleChannel(
            level=env('LOG_SINGLE_LEVEL', 'debug'),
            path=env('LOG_SINGLE_PATH', 'storage/logs/single.log'),
        ),
        'stack': StackChannel(),
        'daily': DailyChannel(
            level=env('LOG_DAILY_LEVEL', 'debug'),
            path=env('LOG_DAILY_PATH', 'storage/logs'),
        ),
        'terminal': TerminalChannel(
            level=env('LOG_TERMINAL_LEVEL', 'info'),
        ),
        'slack': SlackChannel(
            channel=env('LOG_SLACK_CHANNEL', '#bot'),
            emoji=env('LOG_SLACK_EMOJI', ':warning:'),
            username=env('LOG_SLACK_USERNAME', 'Logging Bot'),
            token=env('SLACK_TOKEN', None),
            level=env('LOG_SLACK_LEVEL', 'debug'),
        ),
        'syslog': SyslogChannel(
            path=env('LOG_SYSLOG_PATH', '/var/run/syslog'),
            level=env('LOG_SYSLOG_LEVEL', 'debug'),
        ),
    })
