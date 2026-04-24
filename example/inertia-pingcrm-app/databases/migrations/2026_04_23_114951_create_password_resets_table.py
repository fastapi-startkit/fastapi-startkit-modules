from fastapi_startkit.masoniteorm.migrations import Migration


class CreatePasswordResetsTable(Migration):
    async def up(self):
        """Run the migrations."""
        async with await self.schema.create("password_resets") as table:
            table.string("email").index()
            table.string("token")
            table.timestamp("created_at").nullable()

    async def down(self):
        """Revert the migrations."""
        await self.schema.drop("password_resets")
