import json
from typing import Any, Dict, Optional, Union
from fastapi import Request, Response
from fastapi.responses import JSONResponse, HTMLResponse
from starlette.templating import Jinja2Templates

class Inertia:
    def __init__(self, application):
        self.app = application
        self._shared_data: Dict[str, Any] = {}
        self._version: Optional[str] = None
        self._root_view: str = "index.html"

    def share(self, key: Union[str, Dict[str, Any]], value: Any = None):
        """Share data globally across all components."""
        if isinstance(key, dict):
            self._shared_data.update(key)
        else:
            self._shared_data[key] = value

    def version(self, version: str):
        """Set the current asset version."""
        self._version = version

    def get_version(self) -> Optional[str]:
        """Get the current asset version."""
        return self._version

    def set_root_view(self, root_view: str):
        """Set the root view template name."""
        self._root_view = root_view

    def render(self, request: Request, component: str, props: Optional[Dict[str, Any]] = None) -> Response:
        """Render an Inertia response."""
        props = props or {}
        
        # Merge shared data
        # Note: In a real implementation, we might want to resolve callables here
        all_props = {**self._shared_data, **props}
        
        # Handle Partial Reloads
        partial_component = request.headers.get("X-Inertia-Partial-Component")
        if partial_component == component:
            partial_data = request.headers.get("X-Inertia-Partial-Data")
            if partial_data:
                keys = partial_data.split(",")
                all_props = {k: v for k, v in all_props.items() if k in keys}

        page = {
            "component": component,
            "props": all_props,
            "url": str(request.url.path),
            "version": self._version,
        }

        if request.headers.get("X-Inertia"):
            return JSONResponse(
                content=page,
                headers={
                    "X-Inertia": "true",
                    "Vary": "Accept",
                }
            )

        # Initial render: return HTML root view
        if not self.app.has("templates"):
            raise RuntimeError("Inertia requires 'templates' to be bound in the container for initial rendering.")
            
        templates = self.app.make("templates")
        return templates.TemplateResponse(
            request,
            self._root_view,
            {"page": page}
        )
