from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi_startkit.orm.models import Model


class Factory(ABC):
    model: 'Model'

    @abstractmethod
    def definition(self)->dict:
        ...

    @classmethod
    async def create(cls) -> 'Model':
        model: Model = cls.model
        instance = cls()

        result = await model.create(instance.definition())
        return result
