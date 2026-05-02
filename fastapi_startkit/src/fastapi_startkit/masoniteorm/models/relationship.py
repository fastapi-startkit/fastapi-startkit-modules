from __future__ import annotations

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .model import Model
    from ..collection import Collection


class Relationship:
    __relationship_hidden__ = {}
    __with__ = ()

    def __init__(self, **kwargs):
        self._relationship = {}

    def relationship_loaded(self, key):
        return key in self._relationship

    def get_relationship(self, key) -> Union["Model", "Collection", None]:
        if self.relationship_loaded(key):
            return self._relationship[key]
        return None
