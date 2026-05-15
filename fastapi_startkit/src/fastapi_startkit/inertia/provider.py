import json
from markupsafe import Markup
from fastapi_startkit.providers import Provider
from .inertia import Inertia
from .middleware import InertiaMiddleware


class InertiaProvider(Provider):
    provider_key = "inertia"

    def register(self) -> None:
        self.app.bind("inertia", Inertia)

    def boot(self) -> None:
        self.register_validation_handler()

        self.app.add_middleware(InertiaMiddleware)

        if self.app.has("templates"):
            templates = self.app.make("templates")

            def inertia_helper(page):
                encoded_page = json.dumps(page)
                return Markup(
                    f'<script data-page="app" type="application/json">{encoded_page}</script><div id="app"></div>'
                )

            templates.env.globals["inertia"] = inertia_helper
            templates.env.globals["Inertia"] = self.app.make("inertia")

    def register_validation_handler(self) -> None:
        from fastapi.exceptions import RequestValidationError
        from .exceptions import InertiaValidationHandler

        self.app.exception_manager.register_handler(RequestValidationError, InertiaValidationHandler())
