from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class NotAuthenticated(Exception):
    pass


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
                        "account": {"id": user.account_id, "name": "Acme Corporation"},
                    }
        return await call_next(request)


async def auth(request: Request):
    """FastAPI dependency — raises NotAuthenticated if no user in session."""
    if not getattr(request.state, "user", None):
        raise NotAuthenticated()
