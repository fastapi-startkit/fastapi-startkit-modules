from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.models.user import User
from app.http.schemas.auth import StudentRegistrationRequest, TeacherRegistrationRequest
from app.http.controllers.auth_controller import AuthController

public = APIRouter()

@public.get("/")
async def index():
    return {"message": "Welcome to the Database App Example!"}

@public.get("/users")
async def get_users():
    users = await User.first()
    return JSONResponse({
        "id": users.id,
        "name": users.name,
        "email": users.email,
        "created_at": users.created_at.diff_for_humans() if users else None
    })

@public.post("/register/student")
async def register_student(data: StudentRegistrationRequest):
    return await AuthController.register_student(data)

@public.post("/register/teacher")
async def register_teacher(data: TeacherRegistrationRequest):
    return await AuthController.register_teacher(data)
