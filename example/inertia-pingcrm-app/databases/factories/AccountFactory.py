from fastapi_startkit.masoniteorm.factory import Factory
from app.models.Account import Account


class AccountFactory(Factory):
    model = Account

    def definition(self):
        return {
            "name": self.fake.company(),
        }
