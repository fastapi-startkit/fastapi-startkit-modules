from cleo.commands.command import Command
from cleo.helpers import option


class ServeCommand(Command):
    name = "serve"
    description = "Start the FastAPI server."

    options = [
        option(
            "port",
            "p",
            flag=False,
            default="8000",
            description="The port to serve the application on",
        ),
        option(
            "host",
            None,
            flag=False,
            default="127.0.0.1",
            description="The host to bind to",
        ),
        option(
            "reload",
            "r",
            flag=False,
            default=True,
            description="Enable auto-reload on code changes",
        ),
        option(
            "app",
            "a",
            flag=False,
            default="bootstrap.application:app",
            description="The application to serve",
        ),
    ]

    def handle(self):
        import uvicorn
        from fastapi_startkit.container import Container

        port = int(self.option("port"))
        host = self.option("host")
        app = self.option("app")
        reload = self.option("reload")

        exist = self.is_app_exist()

        kwargs = {
            "host": host,
            "port": port,
            "reload": reload,
            "ws": "websockets-sansio",
        }

        if exist:
            kwargs.update(
                {
                    "app": app,
                    "reload": reload,
                    "factory": True,
                    "reload_excludes": ["*.log", "tests/*"],
                }
            )

            self.line(
                f"<info>Starting Uvicorn server on {host}:{port} [{app}]...</info>"
            )

        else:
            self.line(f"<info>Starting Uvicorn server on {host}:{port}...</info>")
            kwargs.update({"app": Container.instance().fastapi, "reload": False})

        try:
            uvicorn.run(**kwargs)
        except KeyboardInterrupt:
            self.line("<comment>Server stopped manually.</comment>")

    def is_app_exist(self) -> "bool":
        import importlib.util

        app = self.option("app")

        module_name = app.split(":")[0]
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                return True
        except (ImportError, ValueError):
            pass

        self.line(
            "<fg=yellow>Unable to detect the application, run the command with --app={app}</>"
        )

        return False
