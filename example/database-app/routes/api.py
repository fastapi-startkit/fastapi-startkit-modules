from fastapi_startkit.fastapi import Router

from app.students.controllers import auth_controller as student_auth
from app.http.controllers.auth_controller import AuthController

public = Router()

public.post("/register/student", student_auth.register)
public.post("/register/teacher", AuthController.register_teacher)
