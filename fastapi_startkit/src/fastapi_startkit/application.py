import os
from pathlib import Path
from typing import Type, Callable, Any, List

from .container import Container
from .environment.environment import LoadEnvironment
from .configuration.providers import ConfigurationProvider

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from fastapi import FastAPI, APIRouter
    from starlette.middleware.base import BaseHTTPMiddleware

def app() -> 'Container':
    return Container.instance()

class Application(Container):
    DEFAULT_PROVIDERS = [
        ConfigurationProvider,
    ]

    def __init__(self, base_path: str = None,env=None, providers=None):
        super().__init__()

        self.base_path: str = base_path or os.getcwd()
        self.env = env
        self.providers = self.DEFAULT_PROVIDERS + (providers or [])
        self.published_resources = {}
        self.commands = []

        # Set global singleton
        Container.set_instance(self)

        # Boot application
        self.load_environment()
        self.configure_paths()
        self.register_providers()

        self._fastapi: Optional["FastAPI"] = None
        self.load_providers()

    def register_providers(self):
        providers = []
        for provider_data in self.providers:
            config = {}
            if isinstance(provider_data, tuple):
                provider_class, config = provider_data
            else:
                provider_class = provider_data

            provider = provider_class(self, config=config)
            provider.register()
            providers.append(provider)

        self.providers = providers
        return self

    def load_providers(self):
        for provider in self.providers:
            self.resolve(provider.boot)
        return self

    def use_fastapi(self, fastapi: "FastAPI"):
        self._fastapi = fastapi
        return self

    def use_base_path(self, path: str):
        return str(Path(self.base_path) / path)

    def get(self, path: str, **kwargs) -> Callable:
        return self.fastapi.get(path, **kwargs)

    def post(self, path: str, **kwargs) -> Callable:
        return self.fastapi.post(path, **kwargs)

    def put(self, path: str, **kwargs) -> Callable:
        return self.fastapi.put(path, **kwargs)

    def delete(self, path: str, **kwargs) -> Callable:
        return self.fastapi.delete(path, **kwargs)

    def patch(self, path: str, **kwargs) -> Callable:
        return self.fastapi.patch(path, **kwargs)

    def options(self, path: str, **kwargs) -> Callable:
        return self.fastapi.options(path, **kwargs)

    def head(self, path: str, **kwargs) -> Callable:
        return self._fastapi.head(path, **kwargs)

    def trace(self, path: str, **kwargs) -> Callable:
        return self._fastapi.trace(path, **kwargs)

    # Include routers
    def include_router(self, router: "APIRouter", **kwargs):
        self._fastapi.include_router(router, **kwargs)
        return self

    # Add middleware
    def add_middleware(self, middleware_class: Type['BaseHTTPMiddleware'], **options):
        self._fastapi.add_middleware(middleware_class, **options)
        return self

    # Add event handlers (startup/shutdown)
    def add_event_handler(self, event_type: str, func: Callable[..., Any]):
        self.fastapi.add_event_handler(event_type, func)
        return self

    # Mount sub-apps
    def mount(self, path: str, app_instance: "FastAPI", **kwargs):
        self._fastapi.mount(path, app_instance, **kwargs)
        return self

    # Add custom exception handlers
    def add_exception_handler(self, exc_class_or_status_code: Any, handler: Callable[..., Any]):
        self._fastapi.add_exception_handler(exc_class_or_status_code, handler)
        return self

    @property
    def fastapi(self) -> "FastAPI":
        if self._fastapi is None:
            try:
                from fastapi import FastAPI
            except ImportError:
                raise RuntimeError(
                    "FastAPI is not installed. Install it with: pip install fastapi"
                )
            self._fastapi = FastAPI()
        # Making the type hint work
        assert self._fastapi is not None
        return self._fastapi

    def __call__(self, *args, **kwargs):
        return self.fastapi

    def load_environment(self):
        LoadEnvironment(base_path=self.base_path)

    def configure_paths(self):
        self.bind('config.location', os.path.join(self.base_path, "config"))

    def use_config_path(self, path: str = None):
        self.bind('config.location', path)

        return self

    def use_storage_path(self, path: str = None):
        self.bind('storage.location', path)

        return self

    def add_commands(self, commands: List):
        self.commands.extend(commands)

    def handle_command(self):
        from fastapi_startkit.console import ConsoleApplication

        ConsoleApplication(self).handle()
