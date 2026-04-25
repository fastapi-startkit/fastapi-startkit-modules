from fastapi import APIRouter, Request

web = APIRouter()


@web.get("/")
async def index(request: Request):
    from fastapi_startkit.facades import Inertia
    return Inertia.render(request, "Welcome", {
        "user": "Developer",
        "framework": "FastAPI StartKit"
    })


@web.get("/tickets")
async def tickets(request: Request):
    from fastapi_startkit.facades import Inertia
    # Props passed here become available as React component props.
    # Replace with real DB queries when ready.
    return Inertia.render(request, "Tickets", {})


@web.get("/api/health")
async def health():
    return {"status": "healthy"}
