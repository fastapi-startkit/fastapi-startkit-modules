from .db import DB

schema = DB.get_schema_builder()

async def migrate():
    async with (await schema.on('default').create("users") as table):
        table.id()
        table.string("name")
        table.string("email").unique()
        table.timestamp('email_verified_at').nullable()
        table.timestamps()
