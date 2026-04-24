from faker import Faker
from fastapi_startkit.masoniteorm.factory import Factory
from app.models.Contact import Contact

fake = Faker()


class ContactFactory(Factory):
    model = Contact

    def definition(self):
        return {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.unique.email(),
            "phone": fake.phone_number(),
            "address": fake.street_address(),
            "city": fake.city(),
            "region": fake.state(),
            "country": "US",
            "postal_code": fake.postcode(),
        }
