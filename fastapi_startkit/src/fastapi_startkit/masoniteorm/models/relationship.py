class Relationship:
    __relationship_hidden__ = {}
    __with__ = ()

    def __init__(self, **kwargs):
        self._relationship = {}

    def relationship_loaded(self, key):
        return key in self._relationship
