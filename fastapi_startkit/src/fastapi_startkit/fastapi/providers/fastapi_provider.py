from fastapi import FastAPI

from fastapi_startkit.fastapi.commands import ServeCommand
from fastapi_startkit.providers import Provider


class FastAPIProvider(Provider):
    def register(self) -> None:
        """Create a FastAPI instance and register routers."""
        fastapi = FastAPI(
            title="Jobins AI Agent (LangChain)",
            version="1.0.0",
        )

        self.app.use_fastapi(fastapi)

    def boot(self):
        self.commands([ServeCommand])
        self._register_exception_handlers()

    def _register_exception_handlers(self):
        """Wire exception_manager as a catch-all handler for all exceptions."""
        if not self.app.exception_manager:
            return

        exception_manager = self.app.exception_manager

        async def handler(request, exc):
            return await exception_manager.handle(exc, {"request": request})

        self.app.fastapi.add_exception_handler(Exception, handler)
