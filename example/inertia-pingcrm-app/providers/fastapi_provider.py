from pathlib import Path

from fastapi import FastAPI
from starlette.templating import Jinja2Templates

from fastapi_startkit.fastapi import FastAPIProvider as BaseFastAPIProvider


class FastAPIProvider(BaseFastAPIProvider):
    def register(self) -> None:
        fastapi = FastAPI(
            title="Vite Example",
            version="0.1.0",
        )
        self.app.use_fastapi(fastapi)

        # Bind Jinja2Templates so ViteProvider can inject vite() globals into it.
        templates_dir = Path(self.app.base_path) / "templates"
        templates = Jinja2Templates(directory=str(templates_dir))
        self.app.bind("templates", templates)

    def boot(self) -> None:
        super().boot()

        inertia = self.app.make("inertia")
        inertia.share("app_name", "Inertia Demo")
        inertia.version("v1.0.0")

        # Basic Auth sharing
        def resolve_auth(request):
            user = getattr(request.state, "user", None)
            return {"user": user}

        inertia.share("auth", resolve_auth)
        inertia.share("flash", lambda request: {
            "success": request.session.get("flash_success") if "session" in request.scope else None,
            "error": request.session.get("flash_error") if "session" in request.scope else None,
        })
        inertia.share("errors", {})

        from routes.web import web
        self.app.include_router(web)

        # Middleware must be added after include_router() triggers lazy FastAPI creation.
        # The Application resets _fastapi=None after register(), so anything added in
        # register() is discarded. Adding here ensures it lands on the live instance.
        from starlette.middleware.sessions import SessionMiddleware
        from starlette.middleware.base import BaseHTTPMiddleware
        from fastapi import Request

        class AuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next):
                request.state.user = None
                if "session" in request.scope:
                    user_id = request.session.get("user_id")
                    if user_id:
                        from app.models.User import User
                        user = await User.find(user_id)
                        if user:
                            request.state.user = {
                                "id": user.id,
                                "first_name": user.first_name,
                                "last_name": user.last_name,
                                "email": user.email,
                                "role": "Owner" if user.owner else "User",
                                "account": {
                                    "id": user.account_id,
                                    "name": "Acme Corporation"
                                }
                            }

                # Protect routes
                path = request.url.path
                if not request.state.user and not path.startswith(("/login", "/img", "/api/health", "/favicon.ico", "/build")):
                    from fastapi.responses import RedirectResponse
                    return RedirectResponse(url="/login", status_code=303)

                return await call_next(request)

        self.app.add_middleware(AuthMiddleware)
        self.app.add_middleware(SessionMiddleware, secret_key="super-secret-key")