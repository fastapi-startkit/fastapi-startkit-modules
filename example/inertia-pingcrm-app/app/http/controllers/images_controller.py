from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi_startkit.inertia import Inertia

async def show(request: Request):
    return JSONResponse(content={'message': 'images_controller.py@show'})

