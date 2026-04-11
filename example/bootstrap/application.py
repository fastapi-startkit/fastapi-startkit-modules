import logging
from pathlib import Path

from fastapi_startkit.application import Application
from fastapi_startkit.console import ConsoleApplication
from fastapi_startkit.facades import Config
from providers.fastapi_provider import FastAPIProvider
from fastapi_startkit.logging.providers import LogProvider

providers = [
    (LogProvider, {
        'default': 'stack',
        'channels': {
            'stack': {
                'driver': 'stack',
                'channels': ['daily', 'terminal']
            },
            'daily': {
                'driver': 'daily',
                'level': 'debug',
                'path': 'storage/logs'
            },
            'terminal': {
                'driver': 'terminal',
                'level': 'info',
            },
        },
    }),
    FastAPIProvider,
]

app: Application = Application(
    base_path=str(Path().cwd()),
    providers=providers
)

# logger = logging.getLogger(__name__)

# @app.get('/')
# async def hello():
#     logger.info('Hello, World!')
#     return {'message': 'Hello, World!', 'config': Config.get('logging')}
