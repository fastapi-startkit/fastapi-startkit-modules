import inspect
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, List, Optional, Self, Tuple, Union

from faker import Faker

if TYPE_CHECKING:
    from fastapi_startkit.masoniteorm.models import Model

fake = Faker()


class Factory(ABC):
    model: "Model"
    fake: Faker = fake
    _after_making: List[Callable] = []
    _after_creating: List[Callable] = []
    _states: List[Callable] = []
    _has: List[Tuple["Factory", Optional[str]]] = []
    _for: Optional["Factory"] = None
    _count: Optional[int] = None

    def __init__(self):
        self._after_making = []
        self._after_creating = []
        self._states = []
        self._has = []
        self._for = None
        self._count = None

    @abstractmethod
    def definition(self) -> dict: ...

    def configure(self) -> Self:
        return self

    def count(self, n: int) -> Self:
        self._count = n
        return self

    def state(self, callback: Callable) -> Self:
        self._states.append(callback)
        return self

    def has(self, factory: "Factory", relationship: str = None) -> Self:
        self._has.append((factory, relationship))
        return self

    def for_(self, factory: "Factory") -> Self:
        self._for = factory
        return self

    def after_making(self, callback: Callable) -> Self:
        self._after_making.append(callback)
        return self

    def after_creating(self, callback: Callable) -> Self:
        self._after_creating.append(callback)
        return self

    def _apply_states(self, attributes: dict) -> dict:
        for state in self._states:
            if callable(state):
                if inspect.isfunction(state) or inspect.ismethod(state):
                    # Check if it takes attributes
                    sig = inspect.signature(state)
                    if len(sig.parameters) > 0:
                        attributes.update(state(attributes))
                    else:
                        attributes.update(state())
                else:
                    attributes.update(state)
            elif isinstance(state, dict):
                attributes.update(state)
        return attributes

    async def make(self, **overrides) -> Union["Model", List["Model"]]:
        count = self._count or 1
        instances = []

        for _ in range(count):
            attributes = self.definition()
            attributes = self._apply_states(attributes)
            attributes.update(overrides)

            instance = self.model(attributes)

            for callback in self._after_making:
                await callback(instance)

            instances.append(instance)

        return instances if self._count is not None else instances[0]

    async def create(self, **overrides) -> Union["Model", List["Model"]]:
        count = self._count or 1
        results = []

        for _ in range(count):
            attributes = self.definition()
            attributes = self._apply_states(attributes)
            attributes.update(overrides)

            # Handle 'for' relationship
            if self._for:
                parent = await self._for.create()
                # Naive FK: parent_table_singular_id
                foreign_key = f"{parent.__table__[:-1]}_id"
                attributes[foreign_key] = parent.id

            result = await self.model.create(attributes)

            # Handle 'has' relationships
            for factory, relationship in self._has:
                # Naive FK: current_table_singular_id
                foreign_key = f"{self.model.__table__[:-1]}_id"
                await factory.create(**{foreign_key: result.id})

            for callback in self._after_creating:
                await callback(result)

            results.append(result)

        return results if self._count is not None else results[0]

    @classmethod
    def new(cls) -> Self:
        instance = cls()
        return instance.configure()
