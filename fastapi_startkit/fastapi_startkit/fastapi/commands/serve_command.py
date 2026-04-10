from cleo.commands.command import Command
from cleo.io.inputs.option import Option


class ServeCommand(Command):
    """Start the FastAPI server"""

    name = "serve"
    description = "Start the FastAPI server"
    options = [
        Option(
            "port",
            shortcut="p",
            flag=False,
            default="8000",
            description="The port to serve the application on",
        ),
        Option(
            "app",
            shortcut="a",
            flag=False,
            default="bootstrap.application:app",
            description="The application to serve",
        )
    ]

    def handle(self):
        import uvicorn

        port = int(self.option("port"))
        app_module = self.option("app")

        self.line(f"<info>Starting Uvicorn server on port {port} using {app_module}...</info>")

        try:
            uvicorn.run(
                app_module,
                host="127.0.0.1",
                port=port,
                reload=True,
                reload_excludes=[
                    "*.log",
                    "tests/*",
                ],
                ws="websockets-sansio",
                factory=True
            )
        except KeyboardInterrupt:
            self.line("<comment>Server stopped manually.</comment>")
