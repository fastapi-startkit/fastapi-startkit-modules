from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, List

if TYPE_CHECKING:
    from fastapi_startkit.masoniteorm.models import Model


class FactoryBuilder:
    """Fluent builder returned by Factory.new()."""

    def __init__(self, factory_cls: "type[Factory]"):
        self._factory_cls = factory_cls
        self._count: int = 1
        self._states: list[Callable] = []
        self._after_making: list[Callable] = []
        self._after_creating: list[Callable] = []

    def count(self, n: int) -> "FactoryBuilder":
        self._count = n
        return self

    def state(self, callback: Callable) -> "FactoryBuilder":
        self._states.append(callback)
        return self

    def after_making(self, callback: Callable) -> "FactoryBuilder":
        self._after_making.append(callback)
        return self

    def after_creating(self, callback: Callable) -> "FactoryBuilder":
        self._after_creating.append(callback)
        return self

    def _build_attributes(self, overrides: dict) -> dict:
        instance = self._factory_cls()
        attrs = instance.definition()
        for state_fn in self._states:
            result = state_fn(attrs)
            if result:
                attrs.update(result)
        attrs.update(overrides)
        return attrs

    async def create(self, **overrides) -> "Model | list[Model]":
        model_cls = self._factory_cls.model
        results = []

        for _ in range(self._count):
            attrs = self._build_attributes(overrides)
            record = await model_cls.create(attrs)

            for cb in self._after_creating:
                result = cb(record)
                import inspect
                if inspect.isawaitable(result):
                    await result

            results.append(record)

        return results if self._count > 1 else results[0]

    async def make(self, **overrides) -> "Model | list[Model]":
        """Build model instances without persisting."""
        model_cls = self._factory_cls.model
        results = []

        for _ in range(self._count):
            attrs = self._build_attributes(overrides)
            record = model_cls()
            record._attributes = attrs

            for cb in self._after_making:
                result = cb(record)
                import inspect
                if inspect.isawaitable(result):
                    await result

            results.append(record)

        return results if self._count > 1 else results[0]


class Factory(ABC):
    model: "Model"
    _builder: "FactoryBuilder | None" = None

    @abstractmethod
    def definition(self) -> dict: ...

    @classmethod
    def new(cls) -> FactoryBuilder:
        builder = FactoryBuilder(cls)
        # Let subclasses configure the builder via configure()
        instance = cls()
        if hasattr(instance, "configure"):
            instance._builder = builder
            instance.configure()
        return builder

    def state(self, callback: Callable) -> FactoryBuilder:
        """Called from configure() to register a state on the current builder."""
        assert self._builder is not None, "state() must be called inside configure()"
        self._builder.state(callback)
        return self._builder

    def after_making(self, callback: Callable) -> "Factory":
        assert self._builder is not None, "after_making() must be called inside configure()"
        self._builder.after_making(callback)
        return self

    def after_creating(self, callback: Callable) -> "Factory":
        assert self._builder is not None, "after_creating() must be called inside configure()"
        self._builder.after_creating(callback)
        return self
