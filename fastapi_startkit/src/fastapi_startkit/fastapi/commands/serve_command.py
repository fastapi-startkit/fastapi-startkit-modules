from cleo import Command


class ServeCommand(Command):
    """
    Start the FastAPI server.

    serve
        {--p|port=8000 : The port to serve the application on}
        {--a|app=bootstrap.application:app : The application to serve}
    """

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
