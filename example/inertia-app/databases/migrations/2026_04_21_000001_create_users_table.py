"""CreateUsersTable Migration."""

from fastapi_startkit.masoniteorm.migrations import Migration


class CreateUsersTable(Migration):
    async def up(self):
        """Run the migrations."""
        async with await self.schema.create("users") as table:
            table.increments("id")

            table.string("name")
            table.string("email").unique()
            table.string("password")
            table.string("avatar").nullable()          # initials / avatar URL
            table.string("remember_token", 100).nullable()

            table.timestamps()

    async def down(self):
        """Revert the migrations."""
        await self.schema.drop("users")
