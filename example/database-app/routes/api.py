from fastapi_startkit.fastapi import Router

from app.http.controllers.auth_controller import AuthController

public = Router()

public.post("/register/teacher", AuthController.register_teacher)
