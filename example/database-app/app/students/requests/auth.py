from pydantic import BaseModel, Field, EmailStr


class StudentRegistrationRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)
