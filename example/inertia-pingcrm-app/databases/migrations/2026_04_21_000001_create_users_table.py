"""CreateUsersTable Migration."""

from fastapi_startkit.masoniteorm.migrations import Migration


class CreateUsersTable(Migration):
    async def up(self):
        """Run the migrations."""
        async with await self.schema.create("users") as table:
            table.id("id")
            table.integer("account_id").unsigned().index()
            table.string("first_name", 25)
            table.string("last_name", 25)
            table.string("email", 50).unique()
            table.timestamp("email_verified_at").nullable()
            table.string("password").nullable()
            table.boolean("owner").default(False)
            table.string("photo_path", 100).nullable()
            table.string("remember_token", 100).nullable()
            table.timestamps()
            table.soft_deletes()

    async def down(self):
        """Revert the migrations."""
        await self.schema.drop("users")
