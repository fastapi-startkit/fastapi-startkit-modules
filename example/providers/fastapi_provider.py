from fastapi_startkit.fastapi.providers import FastAPIProvider as BaseFastAPIProvider


class FastAPIProvider(BaseFastAPIProvider):
    def boot(self):
        super().boot()
        from routes.api import router
        self.app.fastapi.include_router(router)


