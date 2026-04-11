from .model import Model

class MigrationModel(Model):
    __table__ = "migrations"
    __fillable__ = ["migration", "batch"]
    __timestamps__ = False

    __primary_key__ = "migration_id"
