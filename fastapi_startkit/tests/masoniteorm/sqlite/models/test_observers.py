from fastapi_startkit.masoniteorm.models.model import Model
from ..test_case import TestCase


class TestM:
    pass


class UserObserver:
    def created(self, user):
        TestM.observed_created = True

    def creating(self, user):
        TestM.observed_creating = True

    def saving(self, user):
        TestM.observed_saving = True

    def saved(self, user):
        TestM.observed_saved = True

    def updated(self, user):
        TestM.observed_updated = True

    def updating(self, user):
        TestM.observed_updating = True


class ObservedUser(Model):
    __table__ = "users"
    __timestamps__ = False
    __observers__ = {}
    name: str
    email: str
    is_admin: bool


ObservedUser.observe(UserObserver())


class TestObservers(TestCase):
    async def test_created_is_observed(self):
        await ObservedUser.create({"name": "joe", "email": "obs@test.com", "is_admin": False})
        assert getattr(TestM, "observed_created", False)

    async def test_saving_is_observed(self):
        await ObservedUser.create({"name": "saveable", "email": "save@test.com", "is_admin": False})
        assert getattr(TestM, "observed_saving", False)
        assert getattr(TestM, "observed_saved", False)

    async def test_updating_is_observed(self):
        user = await ObservedUser.create({"name": "updatable", "email": "update@test.com", "is_admin": False})
        await user.update({"name": "updated_name"})
        assert getattr(TestM, "observed_updated", False)
