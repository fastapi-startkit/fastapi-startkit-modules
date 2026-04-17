


class User(Model):
    __timestamps__ = False

    created_at: Carbon = CreatedAtField(fmt="YYYY-MM-DD HH:mm:ss", tz="UTC")
    updated_at: Carbon = UpdatedAtField(fmt="YYYY-MM-DD HH:mm:ss", tz="UTC")
