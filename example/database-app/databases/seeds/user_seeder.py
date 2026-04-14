from fastapi_startkit.masoniteorm.seeds import Seeder
from app.models.user import User

class UserSeeder(Seeder):
    async def run(self):
        await User.first_or_create(
            {"email": "admin@example.com"},
            {"name": "Admin User", "password": "secret"}
        )
        await User.first_or_create(
            {"email": "john@example.com"},
            {"name": "John Doe", "password": "secret"}
        )
