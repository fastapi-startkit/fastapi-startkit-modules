from fastapi import FastAPI
from fastapi_startkit.providers import Provider
from fastapi_startkit.fastapi.commands import ServeCommand


class FastAPIProvider(Provider):
    def register(self) -> None:
        """Create a FastAPI instance and register routers."""
        fastapi = FastAPI(
            title="Jobins AI Agent (LangChain)",
            version="1.0.0",
        )

        self.app.use_fastapi(fastapi)

    def boot(self):
        self.commands([
            ServeCommand
        ])

        """
        Register routes
        
        ```python routes/api.py
        from fastapi import APIRouter
        
        public = APIRouter()
        ```
        
        ```python providers/fastapi_provider.py
        
        class FastAPIServiceProvider(BaseServiceProvider):
            def boot(self):
                from routes.api import public
                
                self.app.use_router(public)
        ```
        """
