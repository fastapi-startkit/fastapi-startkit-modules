from fastapi_startkit.fastapi.providers import FastAPIProvider
from routes.api import public

class FastAPIServiceProvider(FastAPIProvider):
    def boot(self) -> None:
        super().boot()

        # Register routers
        self.app.include_router(public)
