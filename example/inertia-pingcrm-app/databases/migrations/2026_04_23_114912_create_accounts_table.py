from fastapi_startkit.masoniteorm.migrations import Migration


class CreateAccountsTable(Migration):
    async def up(self):
        """Run the migrations."""
        async with await self.schema.create("accounts") as table:
            table.id("id")
            table.string("name", 50)
            table.timestamps()

    async def down(self):
        """Revert the migrations."""
        await self.schema.drop("accounts")
