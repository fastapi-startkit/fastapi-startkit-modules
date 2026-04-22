from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from fastapi import status

class InertiaMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Access the application container
        # The application instance is typically available on the request.app if set,
        # but in this framework it might be better to use the singleton or a property.
        from fastapi_startkit.application import app
        container = app()
        
        if not container.has("inertia"):
            return await call_next(request)
            
        inertia = container.make("inertia")
        
        # 1. Version Check
        if request.headers.get("X-Inertia"):
            client_version = request.headers.get("X-Inertia-Version")
            server_version = inertia.get_version()
            
            # If versions mismatch, return 409 Conflict
            if client_version and server_version and client_version != server_version:
                return Response(
                    status_code=status.HTTP_409_CONFLICT, 
                    headers={"X-Inertia-Location": str(request.url)}
                )

        response = await call_next(request)

        # 2. Redirect Handling (302 -> 303 for non-GET Inertia requests)
        # This ensures the browser performs a GET on the new URL.
        if (
            request.headers.get("X-Inertia") 
            and response.status_code == 302 
            and request.method in ["PUT", "PATCH", "DELETE"]
        ):
            response.status_code = status.HTTP_303_SEE_OTHER

        # 3. Add Vary header
        response.headers["Vary"] = "X-Inertia"
        
        return response
