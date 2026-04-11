import asyncio
from fastapi_startkit.masoniteorm.models.model import Model


class User(Model):
    __table__ = "users"

    id: int
    name: str

async def main():
    import os
    os.environ["DB_CONFIG_PATH"] = "example.config.database"

    # Create the table and a test record
    # builder = User().get_builder()
    # connection = await builder.new_connection()
    # await connection.query("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    # await connection.query("INSERT INTO users (id, name) VALUES (1, 'Test User')")

    # This is for testing the async connection
    user = await User.find(1)
    print(f"Found user: {user.name} (ID: {user.id})")


if __name__ == "__main__":
    asyncio.run(main())
