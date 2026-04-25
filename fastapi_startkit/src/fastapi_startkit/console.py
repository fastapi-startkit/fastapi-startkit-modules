from cleo.application import Application as BaseApplication
from cleo.io.io import IO
from fastapi_startkit.application import Application


class ConsoleApplication(BaseApplication):
    def __init__(self, app: Application):
        super().__init__()
        self.app = app

        # Register commands from Application
        for command in self.app.commands:
            if isinstance(command, type):
                self.add(command())
            else:
                self.add(command)

    def render_error(self, error: Exception, io: IO) -> None:
        self.app.exception_manager.report(error)
        super().render_error(error, io)

    def handle(self):
        self.run()
