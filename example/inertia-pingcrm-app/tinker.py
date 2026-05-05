from dumpdie import dd
from fastapi_startkit.collection import collection
from pydantic import BaseModel, ValidationError, Field, EmailStr


class RegisterRequest(BaseModel):
    name: str = Field(min_length=3)
    email: EmailStr
    password: str


class Error:
    def __init__(self, field: str, error_type: str, inputs: list, message: str, **args):
        self.field = field
        self.error_type = error_type
        self.inputs = inputs
        self.message = message


try:
    RegisterRequest(**{"email": "h"})
except ValidationError as e:
    errors = collection.Collection()
    for error in e.errors():
        print(error)
        err = Error(
            field=error.get('loc')[0],
            message=error.get('msg'),
            error_type=error.get('type'),
            inputs=error.get('inputs'),
        )

        errors.push(err)

    dd(errors)
