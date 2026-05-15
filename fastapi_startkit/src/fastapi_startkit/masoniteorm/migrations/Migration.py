from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class Migration:
    def __init__(self, connection=None, schema=None):
        self.connection = connection

        self.schema = schema
