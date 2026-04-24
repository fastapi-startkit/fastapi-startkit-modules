from fastapi import Request
from fastapi_startkit.facades import Inertia

async def index(request: Request):
    return Inertia.render(request, 'Dashboard/Index', {})

