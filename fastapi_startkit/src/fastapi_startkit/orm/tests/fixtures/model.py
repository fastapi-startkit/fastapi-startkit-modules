from fastapi_startkit.carbon.carbon import Carbon
from fastapi_startkit.orm.models.model import Model
from fastapi_startkit.masoniteorm.models.fields import DateTimeField


class User(Model):
    id: int
    name: str
    email: str

    email_verified_at: Carbon = DateTimeField(fmt="%Y-%m-%d %H:%M:%S", tz="UTC")
