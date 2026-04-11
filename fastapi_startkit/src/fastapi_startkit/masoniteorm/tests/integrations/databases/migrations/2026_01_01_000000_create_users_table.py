from fastapi_startkit.masoniteorm.migrations import Migration

class CreateUsersTable(Migration):
    async def up(self):
        """
        Run the migrations.
        """
        async with await self.schema.create("users") as table:
            table.increments("id")
            table.string("name")
            table.string("username").unique()
            table.string("email").unique()
            table.string("password")
            table.integer("age").nullable()
            table.float("balance").nullable()
            table.json("metadata").nullable()
            table.boolean("is_active").default(True)
            table.text("bio").nullable()
            table.decimal("price", 10, 2).nullable()
            table.timestamps()

    async def down(self):
        """
        Revert the migrations.
        """
        await self.schema.drop("users")
