import hashlib

from fastapi import HTTPException

from app.http.schemas.auth import StudentRegistrationRequest
from app.models import User, Profile


async def register(request: StudentRegistrationRequest):
    existing_user = await User.where("email", request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    password = hashlib.md5(request.password.encode()).hexdigest()
    user = User(
        name=request.name,
        email=request.email,
        password=password,
        role="student",
    )
    await user.save()

    profile = Profile()
    profile.user_id = user.id
    await profile.save()

    return {"message": "Student registered successfully", "user_id": user.id}


def login():
    pass
