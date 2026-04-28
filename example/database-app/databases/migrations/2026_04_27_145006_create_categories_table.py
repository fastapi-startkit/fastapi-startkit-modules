"""CreateCategoriesTable Migration."""

from fastapi_startkit.masoniteorm.migrations import Migration


class CreateCategoriesTable(Migration):
    async def up(self):
        """
        Run the migrations.
        """
        async with await self.schema.create("categories") as table:
            table.increments("id")
            table.string("name")
            table.timestamps()

    async def down(self):
        """
        Revert the migrations.
        """
        await self.schema.drop("categories")
