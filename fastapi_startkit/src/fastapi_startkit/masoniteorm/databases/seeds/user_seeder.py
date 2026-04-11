from ..seeds import Seeder

class UserSeeder(Seeder):
    async def run(self):
        """Run the database seeds."""
        from ...tests.integrations.test_model import User
        
        await User.create(name="Admin", username="admin", email="admin@example.com", password="password")
        await User.create(name="Guest", username="guest", email="guest@example.com", password="password")
