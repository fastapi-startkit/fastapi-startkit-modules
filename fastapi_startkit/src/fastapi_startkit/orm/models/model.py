from fastapi_startkit.carbon import Carbon
from fastapi_startkit.masoniteorm.models.fields import CreatedAtField, UpdatedAtField
from fastapi_startkit.masoniteorm.observers import ObservesEvents
from fastapi_startkit.orm.connections.manager import DatabaseManager
from fastapi_startkit.orm.models.attribute import Attribute
from fastapi_startkit.orm.models.relationship import Relationship


class Model(Attribute, Relationship, ObservesEvents):
    db_manager: 'DatabaseManager' = None

    __observers__ = {}
    __has_events__ = True
    __timestamps__ = True
    __primary_key__ = "id"

    created_at: Carbon = CreatedAtField(fmt="%Y-%m-%d %H:%M:%S", tz="UTC")
    updated_at: Carbon = UpdatedAtField(fmt="%Y-%m-%d %H:%M:%S", tz="UTC")

    def __init__(self, attributes: dict = None, **kwargs):
        super().__init__(attributes, **kwargs)
        self.connection = 'default'
        self._global_scopes = {}
        self.__with__ = {}
        self._exists = False
        self._was_recently_created = False

    def new_query(self):
        return self.db_manager.connection(self.connection).query().set_model(self)

    def __getattr__(self, attribute):
        return self.get_attribute(attribute)

    @classmethod
    def query(cls):
        return cls().new_query()

    async def save(self, options: dict | None = None) -> bool:
        query = self.new_query()

        self.observe_events(self, "saving")

        if self._exists:
            saved = await self.perform_update(query) if self.is_dirty() else True
        else:
            saved = await self.perform_insert(query)

        if saved:
            self.finish_saving(options)

        return saved

    def finish_saving(self, options: dict | None = None):
        self.observe_events(self, "saved")
        self.sync_original()

    async def perform_insert(self, query) -> bool:
        attributes = self.get_attributes_for_insert()

        inserted_id = await query.insert(attributes)

        # Store the auto-generated primary key so subsequent saves do an UPDATE
        if inserted_id is not None:
            self._dirty_attributes[self.__primary_key__] = inserted_id

        self._exists = True
        self._was_recently_created = True
        self.observe_events(self, "created")
        return True

    async def perform_update(self, query) -> bool:
        dirty = self.get_dirty()
        if not dirty:
            return True

        pk_value = self.get_attribute(self.__primary_key__)
        await query.where(self.__primary_key__, pk_value).update(dirty)

        self.observe_events(self, "updated")
        return True

    def sync_original(self):
        self._attributes = self.get_attributes()
        self._dirty_attributes = {}

    def get_attributes(self) -> dict:
        return {**self._attributes, **self._dirty_attributes}
