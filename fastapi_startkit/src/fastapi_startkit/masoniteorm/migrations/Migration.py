from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi_startkit.masoniteorm import DatabaseManager


class Migration:
    def __init__(self, connection=None, schema=None):
        self.connection = connection

        self.schema = schema
