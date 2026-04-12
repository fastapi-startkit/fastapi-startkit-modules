from fastapi_startkit.masoniteorm.seeds import Seeder
from app.models.User import User

class UserSeeder(Seeder):
    async def run(self):
        await User.create(
            name="Admin User",
            email="admin@example.com",
            password="secret"
        )
        await User.create(
            name="John Doe",
            email="john@example.com",
            password="secret"
        )
