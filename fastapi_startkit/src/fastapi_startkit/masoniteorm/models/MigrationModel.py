from fastapi_startkit.masoniteorm.models import Model


class MigrationModel(Model):
    __table__ = "migrations"
    __timestamps__ = False
    __primary_key__ = "migration_id"

    migration: str
    batch: int
