from cleo import Application as BaseApplication
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

    def handle(self):
        self.run()
