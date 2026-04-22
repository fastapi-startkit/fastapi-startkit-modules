import json
from fastapi_startkit.providers import Provider
from .inertia import Inertia
from .middleware import InertiaMiddleware

class InertiaProvider(Provider):
    provider_key = "inertia"

    def register(self) -> None:
        """Bind Inertia class to the container."""
        self.app.bind("inertia", Inertia(self.app))

    def boot(self) -> None:
        """Configure template globals and middleware."""
        # 1. Register Middleware
        # We add it to the FastAPI instance via the application helper
        self.app.add_middleware(InertiaMiddleware)

        # 2. Register Template Globals
        if self.app.has("templates"):
            templates = self.app.make("templates")
            
            try:
                from markupsafe import Markup
            except ImportError:
                Markup = str

            def inertia_helper(page):
                """Jinja2 helper to render the root div for Inertia."""
                encoded_page = json.dumps(page)
                # Ensure single quotes are used for the attribute to avoid conflict with JSON double quotes
                return Markup(f'<div id="app" data-page=\'{encoded_page}\'></div>')

            templates.env.globals["inertia"] = inertia_helper
            
            # Also share the inertia instance itself if needed
            templates.env.globals["Inertia"] = self.app.make("inertia")
