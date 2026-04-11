import traceback

from fastapi_startkit.application import app
from fastapi_startkit.logging.channels import BaseChannel


class Logger:
    instance = None

    def __init__(self):
        self.app = app()
        self.logger: BaseChannel = self.app.make('logger')

    @classmethod
    def logger_info(cls) -> str:
        frame = None
        for current_frame in reversed(traceback.extract_stack()):
            if "logger.py" not in current_frame.filename:
                frame = current_frame
                break
        if not frame:
            return ""
        filename = frame.filename
        lineno = frame.lineno
        return f'{filename}:{str(lineno)} - '

    @classmethod
    def init(cls) -> BaseChannel:
        if cls.instance:
            return cls.instance.logger
        cls.instance = Logger()
        return cls.instance.logger

    @classmethod
    def emergency(cls, message: str, *args, **kwargs):
        Logger.init().emergency(cls.logger_info() + message, *args, **kwargs)

    @classmethod
    def alert(cls, message: str, *args, **kwargs):
        Logger.init().alert(cls.logger_info() + message, *args, **kwargs)

    @classmethod
    def critical(cls, message: str, *args, **kwargs):
        Logger.init().critical(cls.logger_info() + message, *args, **kwargs)

    @classmethod
    def error(cls, message: str, *args, **kwargs):
        Logger.init().error(cls.logger_info() + message, *args, **kwargs)

    @classmethod
    def warning(cls, message: str, *args, **kwargs):
        Logger.init().warning(cls.logger_info() + message, *args, **kwargs)

    @classmethod
    def notice(cls, message: str, *args, **kwargs):
        Logger.init().notice(cls.logger_info() + message, *args, **kwargs)

    @classmethod
    def info(cls, message: str, *args, **kwargs):
        Logger.init().info(cls.logger_info() + message, *args, **kwargs)

    @classmethod
    def debug(cls, message: str, *args, **kwargs):
        Logger.init().debug(cls.logger_info() + message, *args, **kwargs)
