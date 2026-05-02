from fastapi_startkit.masoniteorm.models import registry
from ..collection import Collection
from .BaseRelationship import BaseRelationship


class HasManyThrough(BaseRelationship):
    """HasManyThrough Relationship Class."""

    def __init__(
        self,
        fn=list[str],
        local_foreign_key=None,
        other_foreign_key=None,
        local_owner_key=None,
        other_owner_key=None,
    ):
        self.fn = lambda x: [registry.Registry.resolve(class_str) for class_str in fn]

        self.local_key = local_foreign_key
        self.foreign_key = other_foreign_key
        self.local_owner_key = local_owner_key or "id"
        self.other_owner_key = other_owner_key or "id"
        self.attribute = fn[0].lower()
        self.distant_builder = None
        self.intermediary_builder = None

    def _init_builders(self):
        """Lazily initialize builders when a live DB connection is available."""
        if self.distant_builder is None or self.intermediary_builder is None:
            relationship1 = self.fn(self)[0]()
            relationship2 = self.fn(self)[1]()
            self.distant_builder = relationship1.get_builder()
            self.intermediary_builder = relationship2.get_builder()
            self.set_keys(self.distant_builder, self.intermediary_builder, self.attribute)

    def _fresh_builders(self):
        """Return fresh (unmodified) builders — required for methods that mutate them."""
        relationship1 = self.fn(self)[0]()
        relationship2 = self.fn(self)[1]()
        distant = relationship1.get_builder()
        intermediary = relationship2.get_builder()
        self.set_keys(distant, intermediary, self.attribute)
        return distant, intermediary

    def __set_name__(self, owner, name):
        self.attribute = name

    def __getattr__(self, attribute):
        relationship = self.fn(self)[0]()
        return getattr(relationship.get_builder(), attribute)

    def set_keys(self, distant_builder, intermediary_builder, attribute):
        self.local_key = self.local_key or "id"
        self.foreign_key = self.foreign_key or f"{attribute}_id"
        self.local_owner_key = self.local_owner_key or "id"
        self.other_owner_key = self.other_owner_key or "id"
        return self

    def __get__(self, instance, owner):
        """This method is called when the decorated method is accessed.

        Arguments:
            instance {object|None} -- The instance we called.
                If we didn't call the attribute and only accessed it then this will be None.

            owner {object} -- The current model that the property was accessed on.

        Returns:
            object -- Either returns a builder or a hydrated model.
        """
        if instance is None or not instance.is_loaded():
            return self

        self._init_builders()

        if self.attribute in instance._relationships:
            return instance._relationships[self.attribute]

        distant, intermediary = self._fresh_builders()
        return self.apply_related_query(distant, intermediary, instance)

    def apply_related_query(self, distant_builder, intermediary_builder, owner):
        """
        Apply the query to return a Collection of data for the distant models to be hydrated with.

        Method is used when accessing a relationship on a model if its not
        already eager loaded

        Arguments
            distant_builder (QueryBuilder): QueryBuilder attached to the distant table
            intermediate_builder (QueryBuilder): QueryBuilder attached to the intermediate (linking) table
            owner (Any): the model this relationship is starting from

        Returns
            Collection: Collection of  dicts which will be used for hydrating models.
        """
        distant_table = distant_builder.get_table_name()
        intermediate_table = intermediary_builder.get_table_name()

        return (
            self.distant_builder.select(
                f"{distant_table}.*, {intermediate_table}.{self.local_key}"
            )
            .join(
                f"{intermediate_table}",
                f"{intermediate_table}.{self.foreign_key}",
                "=",
                f"{distant_table}.{self.other_owner_key}",
            )
            .where(
                f"{intermediate_table}.{self.local_key}",
                getattr(owner, self.local_owner_key),
            )
            .get()
        )

    def relate(self, related_model):
        distant, intermediary = self._fresh_builders()
        return distant.join(
            f"{intermediary.get_table_name()}",
            f"{intermediary.get_table_name()}.{self.foreign_key}",
            "=",
            f"{distant.get_table_name()}.{self.other_owner_key}",
        ).where(
            f"{intermediary.get_table_name()}.{self.local_key}",
            getattr(related_model, self.local_owner_key),
        )

    def get_builder(self):
        return self.distant_builder

    def make_builder(self, eagers=None):
        builder = self.get_builder().with_(eagers)
        return builder

    def register_related(self, key, model, collection):
        """
        Attach the related model to source models attribute

        Arguments
            key (str): The attribute name
            model (Any): The model instance
            collection (Collection): The data for the related models

        Returns
            None
        """
        related = collection.get(getattr(model, self.local_owner_key), None)
        if related and not isinstance(related, Collection):
            related = Collection(related)

        model.add_relation({key: related if related else None})

    async def get_related(self, current_builder, relation, eagers=None, callback=None):
        """
        Get a Collection to hydrate the models for the distant table with
        Used when eager loading the model attribute

        Arguments
            current_builder (QueryBuilder): The source models QueryBuilder object
            relation (HasManyThrough): this relationship object
            eagers (Any):
            callback (Any):

        Returns
             Collection the collection of dicts to hydrate the distant models with
        """
        distant_builder, intermediary_builder = self._fresh_builders()
        distant_table = distant_builder.get_table_name()
        intermediate_table = intermediary_builder.get_table_name()

        if callback:
            callback(current_builder)

        distant_builder.select(
            f"{distant_table}.*, {intermediate_table}.{self.local_key}"
        ).join(
            f"{intermediate_table}",
            f"{intermediate_table}.{self.foreign_key}",
            "=",
            f"{distant_table}.{self.other_owner_key}",
        )

        if isinstance(relation, Collection):
            return await distant_builder.where_in(
                f"{intermediate_table}.{self.local_key}",
                Collection(relation._get_value(self.local_owner_key)).unique(),
            ).get()
        else:
            return await distant_builder.where(
                f"{intermediate_table}.{self.local_key}",
                getattr(relation, self.local_owner_key),
            ).get()

    def query_has(self, current_builder, method="where_exists"):
        distant_builder, intermediary_builder = self._fresh_builders()
        distant_table = distant_builder.get_table_name()
        intermediate_table = intermediary_builder.get_table_name()

        getattr(current_builder, method)(
            distant_builder.join(
                f"{intermediate_table}",
                f"{intermediate_table}.{self.foreign_key}",
                "=",
                f"{distant_table}.{self.other_owner_key}",
            ).where_column(
                f"{intermediate_table}.{self.local_key}",
                f"{current_builder.get_table_name()}.{self.local_owner_key}",
            )
        )

        return distant_builder

    def query_where_exists(self, current_builder, callback, method="where_exists"):
        distant_builder, intermediary_builder = self._fresh_builders()
        distant_table = distant_builder.get_table_name()
        intermediate_table = intermediary_builder.get_table_name()

        getattr(current_builder, method)(
            distant_builder.join(
                f"{intermediate_table}",
                f"{intermediate_table}.{self.foreign_key}",
                "=",
                f"{distant_table}.{self.other_owner_key}",
            )
            .where_column(
                f"{intermediate_table}.{self.local_key}",
                f"{current_builder.get_table_name()}.{self.local_owner_key}",
            )
            .when(callback, lambda q: callback(q))
        )

    def get_with_count_query(self, current_builder, callback):
        distant_builder, intermediary_builder = self._fresh_builders()
        distant_table = distant_builder.get_table_name()
        intermediate_table = intermediary_builder.get_table_name()

        if not current_builder._columns:
            current_builder.select("*")

        return_query = current_builder.add_select(
            f"{self.attribute}_count",
            lambda q: (
                q.count("*")
                .join(
                    f"{intermediate_table}",
                    f"{intermediate_table}.{self.foreign_key}",
                    "=",
                    f"{distant_table}.{self.other_owner_key}",
                )
                .where_column(
                    f"{intermediate_table}.{self.local_key}",
                    f"{current_builder.get_table_name()}.{self.local_owner_key}",
                )
                .table(distant_table)
                .when(
                    callback,
                    lambda q: q.where_in(
                        self.foreign_key,
                        callback(distant_builder.select(self.other_owner_key)),
                    ),
                )
            ),
        )

        return return_query

    def map_related(self, related_result):
        return related_result.group_by(self.local_key)
