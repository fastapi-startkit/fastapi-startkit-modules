from fastapi_startkit.fastapi import Router

from app.students.controllers import auth_controller

router = Router()

router.post("/students/register", auth_controller.register)
router.get("/students/login", auth_controller.login)
