import importlib
from typing import get_type_hints

class BaseRelationship:
    def __init__(self, fn=None, local_key=None, foreign_key=None):
        self._name = None
        self._owner = None
        self._model = None

        if callable(fn) and not isinstance(fn, type):
            self.fn = fn
            self.local_key = local_key
            self.foreign_key = foreign_key
        else:
            self.fn = None
            self._model = fn
            self.local_key = local_key
            self.foreign_key = foreign_key

    def __set_name__(self, owner, name):
        """This method is called right after the decorator is registered.

        At this point we finally have access to the model cls

        Arguments:
            name {object} -- The model class.
        """
        self._name = name
        self._owner = owner

    def __call__(self, fn=None, *args, **kwargs):
        """This method is called when the decorator contains arguments.

        When you do something like this:

        @belongs_to('id', 'user_id').

        In this case, the {fn} argument will be the callable.
        """
        if callable(fn):
            self.fn = fn

        return self


    def __get__(self, instance, owner):
        """
        This method is called when the decorated method is accessed.

        Arguments:
            instance {object|None} -- The instance we called.
                If we didn't call the attribute and only accessed it then this will be None.

            owner {object} -- The current model that the property was accessed on.

        Returns:
            object -- Either returns a builder or a hydrated model.
        """
        if instance is None:
            return self

        attribute = self._name or (self.fn.__name__ if self.fn else None)
        if not attribute:
            raise AttributeError("Relationship attribute name could not be determined")

        if attribute in instance._relationships:
            return instance._relationships[attribute]

        self.set_keys(instance, attribute)

        if self.fn:
            relationship = self.fn(instance)()
            builder = relationship.builder
        else:
            model = self.resolve_model(owner)
            if not model:
                raise ValueError(f"Could not resolve related model for relationship '{attribute}'")
            builder = model().get_builder()

        self._related_builder = builder

        if not instance.is_loaded():
            return self

        return self.apply_query(self._related_builder, instance)

    def resolve_model(self, owner):
        if self._model and not isinstance(self._model, str):
            return self._model

        # Try to infer from type hints if _model is not set
        if not self._model:
            try:
                hints = get_type_hints(owner)
                hint = hints.get(self._name)
                if hint:
                    self._model = hint
            except Exception:
                pass

        # If it's a string, attempt to resolve via Registry
        if isinstance(self._model, str):
            from ..models.registry import Registry
            try:
                self._model = Registry.resolve(self._model)
                return self._model
            except ValueError:
                pass

            # Fallback to module lookup if registry fails
            try:
                module = importlib.import_module(owner.__module__)
                self._model = getattr(module, self._model, None)
            except (ImportError, AttributeError):
                pass

        return self._model

    def get_builder(self):
        # If _related_builder is already set (by __get__ on instance), use it
        if hasattr(self, "_related_builder") and self._related_builder:
            return self._related_builder
            
        # Otherwise resolve the model and get its builder
        model = self.resolve_model(self._owner)
        if not model:
            # Fallback for polymorphic relationships that don't have a single _model
            if hasattr(self, "polymorphic_builder"):
                 return self.polymorphic_builder
            # Attempt to resolve from name if owner is missing (e.g. dynamically added relationships)
            return None
            
        instance = model()
        builder = instance.get_builder()
        self._related_builder = builder
        return self._related_builder

    def make_builder(self, eagers=None):
        builder = self.get_builder()
        if not builder:
            return None
        return builder.with_(eagers or [])
        if self.fn:
            relationship = self.fn(self)()
            return getattr(relationship.builder, attribute)
        
        model = self.resolve_model(self._owner)
        if model:
            return getattr(model().get_builder(), attribute)
        
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{attribute}'")

    def apply_query(self, foreign, owner):
        """Return a dictionary to hydrate the model with

        Arguments:
            foreign {oject} -- The relationship object
            owner {object} -- The current model oject.

        Returns:
            dict -- A dictionary of data which will be hydrated.
        """
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'apply_query' method"
        )

    def query_where_exists(self, builder, callback, method="where_exists"):
        """Adds a criteria clause to the query filter for existing related records"""
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'query_where_exists' method"
        )

    def joins(self, builder, clause=None):
        """Helper method for adding join clauses to a relationship"""
        other_table = self.get_builder().get_table_name()
        local_table = builder.get_table_name()
        return builder.join(
            other_table,
            f"{local_table}.{self.local_key}",
            "=",
            f"{other_table}.{self.foreign_key}",
            clause=clause,
        )

    def get_with_count_query(self, builder, callback):
        """Adds a clause to the query to get the record count of the relationship"""
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'get_with_count_query' method"
        )

    def attach(self, current_model, related_record):
        """Link a related model to the current model"""
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'attach' method"
        )

    def get_related(self, query, relation, eagers=None, callback=None):
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'get_related' method"
        )

    def relate(self, related_record):
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'relate' method"
        )

    def detach(self, current_model, related_record):
        """Unlink a related model from the current model"""
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'detach' method"
        )

    def attach_related(self, current_model, related_record):
        """Unlink a related model from the current model"""
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'attach_related' method"
        )

    def detach_related(self, current_model, related_record):
        """Unlink a related model from the current model"""
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'detach_related' method"
        )

    def query_has(self, current_query_builder, method="where_exists"):
        """Adds a clause to the query to chek if a rwlarion exists"""
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'query_has' method"
        )

    def map_related(self, related_result):
        klass = self.__class__.__name__
        raise NotImplementedError(
            f"{klass} relationship does not implement the 'related_result' method"
        )
