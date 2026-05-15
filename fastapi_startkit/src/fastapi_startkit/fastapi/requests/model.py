import inspect

from fastapi import Form
from fastapi.params import Query as QueryParam
from pydantic import BaseModel


class RequestModel(BaseModel):
    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        super().__pydantic_init_subclass__(**kwargs)

        params = []
        for name, field in cls.model_fields.items():
            if isinstance(field, QueryParam):
                default = field
            elif field.is_required():
                default = Form(...)
            else:
                default = Form(default=field.default)

            params.append(
                inspect.Parameter(
                    name,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=default,
                    annotation=field.annotation,
                )
            )

        cls.__signature__ = inspect.Signature(params)

    def validated(self) -> dict:
        return {k: v for k, v in self.model_dump().items() if v}
