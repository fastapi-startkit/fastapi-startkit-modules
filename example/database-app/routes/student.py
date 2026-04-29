from fastapi_startkit.fastapi import Router

from app.students.controllers.registration import register
from app.students.controllers.auth import login

router = Router()

router.post("/students/register", register)
router.get("/students/login", login)
