from fastapi_startkit.fastapi.exceptions import HTTPExceptionHandler, ValidationExceptionHandler
from fastapi import FastAPI

from fastapi_startkit.fastapi.commands import ServeCommand
from fastapi_startkit.fastapi.config import FastAPIConfig
from fastapi_startkit.providers import Provider


class FastAPIProvider(Provider):
    def register(self) -> None:
        """Create a FastAPI instance and register routers."""
        # Register default FastAPI server config if not already set by user config
        config = self.app.make("config")
        if not config.has("fastapi"):
            config.set("fastapi", FastAPIConfig())

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
        from fastapi import HTTPException
        from fastapi.exceptions import RequestValidationError

        exception_manager = self.app.exception_manager
        exception_manager.register_handler(Exception, HTTPExceptionHandler())
        exception_manager.register_handler(HTTPException, HTTPExceptionHandler())
        exception_manager.register_handler(RequestValidationError, ValidationExceptionHandler())

        async def handler(request, exc):
            return await exception_manager.handle(exc, {"request": request})

        # FastAPI registers its own handlers for these two types internally,
        # so they must be overridden explicitly
        self.app.fastapi.add_exception_handler(HTTPException, handler)
        self.app.fastapi.add_exception_handler(RequestValidationError, handler)
        self.app.fastapi.add_exception_handler(Exception, handler)
