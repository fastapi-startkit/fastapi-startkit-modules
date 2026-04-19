from fastapi_startkit.masoniteorm.query.EagerRelation import EagerRelations

class Relationship:
    __relationship_hidden__ = {}

    def __init__(self, **kwargs):
        self._relationship = {}
        self._eager_relation = EagerRelations()

    def relationship_loaded(self, key):
        return key in self._relationship
