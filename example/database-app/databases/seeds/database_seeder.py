from fastapi_startkit.masoniteorm.seeds import Seeder
from .user_seeder import UserSeeder
from .post_seeder import PostSeeder

class DatabaseSeeder(Seeder):
    async def run(self):
        await self.call(UserSeeder)
        await self.call(PostSeeder)
