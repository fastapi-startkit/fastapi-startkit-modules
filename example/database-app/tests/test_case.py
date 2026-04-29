from abc import ABC
from typing import TYPE_CHECKING

from fastapi_startkit.fastapi.testing import HttpTestCase

if TYPE_CHECKING:
    from fastapi_startkit.application import Application


class TestCase(HttpTestCase, ABC):
    def get_application(self) -> 'Application':
        from bootstrap.application import app
        return app
