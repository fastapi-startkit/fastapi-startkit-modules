from faker import Faker
from fastapi_startkit.masoniteorm.factory import Factory
from app.models.Organization import Organization

fake = Faker()


class OrganizationFactory(Factory):
    model = Organization

    def definition(self):
        return {
            "name": fake.company(),
            "email": fake.company_email(),
            "phone": fake.phone_number(),
            "address": fake.street_address(),
            "city": fake.city(),
            "region": fake.state(),
            "country": "US",
            "postal_code": fake.postcode(),
        }
