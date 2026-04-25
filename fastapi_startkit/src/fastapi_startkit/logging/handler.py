import logging


class LoggingHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        from fastapi_startkit.logging.logger import Logger

        Logger.log(record.levelname, self.format(record))

    @staticmethod
    def install():
        root_logger = logging.getLogger()
        if not any(isinstance(h, LoggingHandler) for h in root_logger.handlers):
            root_logger.addHandler(LoggingHandler())
            root_logger.setLevel(logging.DEBUG)
