import typing
from typing import Annotated, Any, List

from dumpdie import dd
from pydantic import GetCoreSchemaHandler, BaseModel, ValidationError
from pydantic_core import core_schema


class Rule:
    def __init__(self, message: Any = None):
        self.custom_message = message

    def format_message(self, default: str, value: Any, info: Any = None) -> str:
        if self.custom_message is None:
            return default
        if callable(self.custom_message):
            field_name = (
                info.field_name if info and hasattr(info, "field_name") else "field"
            )
            data = info.data if info and hasattr(info, "data") else {}
            return self.custom_message(field_name, value, data)
        return self.custom_message

    def __call__(self, value: Any, info: Any = None) -> Any:
        return value


class Required(Rule):
    def __call__(self, value: Any, info: Any = None) -> Any:
        if value is None or value == "":
            raise ValueError(self.format_message("Field is required", value, info))
        return value


class Unique(Rule):
    def __init__(self, table: str, column: str, message: str = None):
        super().__init__(message)
        self.table = table
        self.column = column

    def __call__(self, value: Any, info: Any = None) -> Any:
        # if db_exists(self.table, self.column, value):
        #     raise ValueError(self.custom_message or f"{self.column} must be unique")
        return value


class Max(Rule):
    def __init__(self, limit: int, message: str = None):
        super().__init__(message)
        self.limit = limit

    def __call__(self, value: Any, info: Any = None) -> Any:
        if value is not None and len(str(value)) > self.limit:
            raise ValueError(self.custom_message or f"Max length is {self.limit}")
        return value


class Min(Rule):
    def __init__(self, limit: int, message: str = None):
        super().__init__(message)
        self.limit = limit

    def __call__(self, value: Any, info: Any = None) -> Any:
        if value is not None and len(str(value)) < self.limit:
            raise ValueError(self.custom_message or f"Min length is {self.limit}")
        return value


class SameAs(Rule):
    def __init__(self, other_field: str, message: str = None):
        super().__init__(message)
        self.other_field = other_field

    def __call__(self, value: Any, info: Any = None) -> Any:
        if info is None or not hasattr(info, 'data') or info.data is None:
            return value

        if self.other_field not in info.data:
            return value

        if value != info.data[self.other_field]:
            raise ValueError(self.custom_message or f"Does not match {self.other_field}")
        return value


class RequiredIf(Rule):
    def __init__(self, other_field: str, expected_value: Any, message: str = None):
        super().__init__(message)
        self.other_field = other_field
        self.expected_value = expected_value

    def __call__(self, value: Any, info: Any = None) -> Any:
        if info is None or not hasattr(info, "data") or info.data is None:
            return value

        other_value = info.data.get(self.other_field)
        if other_value == self.expected_value:
            if value is None or value == "":
                raise ValueError(
                    self.custom_message
                    or f"Field is required when {self.other_field} is {self.expected_value}"
                )
        return value


class EmailRule(Rule):
    def __call__(self, value: Any, info: Any = None) -> Any:
        if value:
            import re
            # Simple but effective email regex
            regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(regex, str(value)):
                raise ValueError("Invalid email address")
        return value


class FieldBuilder:
    def __init__(self):
        self.rules: List[Rule] = []
        self._is_nullable = False
        self._is_required = False

    def required(self, msg: Any = None):
        self.rules.append(Required(message=msg))
        self._is_required = True
        return self

    def nullable(self):
        self._is_nullable = True
        return self

    def unique(self, table="users", column="email", msg: Any = None):
        self.rules.append(Unique(table, column, message=msg))
        return self

    def string(self):
        # The schema already ensures it's a string via handler(source_type)
        return self

    def max(self, limit: int, msg: Any = None):
        self.rules.append(Max(limit, message=msg))
        return self

    def min(self, limit: int, msg: Any = None):
        self.rules.append(Min(limit, message=msg))
        return self

    def email(self, msg: Any = None):
        self.rules.append(EmailRule(message=msg))
        return self

    def same_as(self, other_field: str, msg: Any = None):
        self.rules.append(SameAs(other_field, message=msg))
        return self

    def required_if(self, other_field: str, value: Any, msg: Any = None):
        self.rules.append(RequiredIf(other_field, value, message=msg))
        return self

    def password(self):
        # Default password rules
        self.min(8)
        return self

    def msg(self, message: str):
        if self.rules:
            self.rules[-1].custom_message = message
        return self

    def add(self, rule: Any):
        self.rules.append(rule)
        return self

    def __get_pydantic_core_schema__(self, source_type: Any, handler: GetCoreSchemaHandler):
        rules = self.rules.copy()

        def validate(value: Any, info: core_schema.ValidationInfo) -> Any:
            for rule in rules:
                value = rule(value, info)
            return value

        # Dynamically get the schema for the actual type hint (str, bool, etc.)
        schema = handler(source_type)

        # Detect if the type hint itself is nullable (e.g., str | None)
        origin = typing.get_origin(source_type)
        args = typing.get_args(source_type)
        is_type_nullable = False
        if origin in (typing.Union, getattr(typing, "UnionType", None)):
            if type(None) in args:
                is_type_nullable = True

        # We must allow None to pass through the base type schema
        # so it can reach our validation rules.
        schema = core_schema.chain_schema([
            core_schema.nullable_schema(handler(source_type)),
            core_schema.with_info_plain_validator_function(validate),
        ])

        if self._is_nullable or is_type_nullable or self._is_required:
            return core_schema.with_default_schema(schema, default=None, validate_default=True)

        return schema


class Email(FieldBuilder):
    def __init__(self):
        super().__init__()
        self.rules.append(EmailRule())


class Field(FieldBuilder):
    pass


class CustomCaptch(Rule):
    def __call__(self, value: Any, info: Any = None) -> Any:
        if value is None:
            return value
        if value != "1234":
            raise ValueError("Invalid captcha")
        return value


class Error:
    def __init__(self, field: str, error_type: str, message: str, inputs: Any = None):
        self.field = field
        self.error_type = error_type
        self.message = message
        self.inputs = inputs

    def __repr__(self):
        return f"Error(field={self.field!r}, message={self.message!r})"


class MessageBag:
    def __init__(self, errors: List[Error] = None):
        self._errors = errors or []

    def push(self, error: Error):
        self._errors.append(error)

    def all(self):
        return self._errors

    def to_dict(self):
        errors_dict = {}
        for error in self._errors:
            if error.field not in errors_dict:
                errors_dict[error.field] = []
            errors_dict[error.field].append(error.message)

        total_errors = len(self._errors)
        message = ""
        if total_errors > 0:
            first_msg = self._errors[0].message
            if total_errors > 1:
                message = f"{first_msg} (and {total_errors - 1} more errors)"
            else:
                message = first_msg

        return {
            "message": message,
            "errors": errors_dict
        }

    def __repr__(self):
        import json
        return json.dumps(self.to_dict(), indent=4)


class RegisterUser(BaseModel):
    email: Annotated[str, Email().unique().required()] = None
    username: Annotated[str, Field().required(msg=lambda field, value, inputs: f"{field} is required but you provided {value!r}").string().max(10).min(3)]
    password: Annotated[str, Field().required().password()] = None
    password_confirmation: Annotated[str, Field().required().same_as("password")] = None
    captcha: Annotated[str | None, Field().add(CustomCaptch())] = None
    is_business: Annotated[bool | None, Field()] = None
    tax_id: Annotated[Any, Field().required_if("is_business", True)] = None



# dd(RegisterUser.model_json_schema())

if __name__ == "__main__":
    # Test valid data
    print("Testing valid data...")
    try:
        valid = RegisterUser.model_validate({
            "email": "test@example.com",
            "password": "password123",
            "password_confirmation": "password123",
            "captcha": "1234"
        })
        print("Valid data passed successfully:")
    except Exception as e:
        from dumpdie import dump

        dump()
        print("Valid data failed unexpectedly:")

    # Test invalid email
    print("\nTesting invalid email...")
    try:
        RegisterUser.model_validate({"email": "invalid-email", "password": "password1", "password_confirmation": "password"})
    except ValidationError as e:
        print("Caught expected validation error bag:")
        bag = MessageBag()
        for error in e.errors():
            bag.push(Error(
                field=".".join(str(l) for l in error.get("loc")),
                message=error.get("msg"),
                error_type=error.get("type"),
                inputs=error.get("input"),
            ))
        dd(bag.to_dict())

    # Test password mismatch
    print("\nTesting password mismatch...")
    try:
        RegisterUser.model_validate({
            "email": "test@example.com",
            "username": "johndoe",
            "password": "password123",
            "password_confirmation": "password456"
        })
    except ValidationError as e:
        print("Caught expected password mismatch error bag:")
        bag = MessageBag()
        for error in e.errors():
            bag.push(Error(
                field=".".join(str(l) for l in error.get("loc")),
                message=error.get("msg"),
                error_type=error.get("type"),
                inputs=error.get("input"),
            ))
        dd(bag.to_dict())

    # Test required_if
    print("\nTesting required_if...")
    try:
        RegisterUser.model_validate({
            "email": "test@example.com",
            "username": "johndoe",
            "password": "password123",
            "password_confirmation": "password123",
            "captcha": "1234",
            "is_business": True,
            "tax_id": "" # Should fail
        })
    except ValidationError as e:
        print("Caught expected required_if error bag:")
        bag = MessageBag()
        for error in e.errors():
            bag.push(Error(
                field=".".join(str(l) for l in error.get("loc")),
                message=error.get("msg"),
                error_type=error.get("type"),
                inputs=error.get("input"),
            ))
        dd(bag.to_dict())
