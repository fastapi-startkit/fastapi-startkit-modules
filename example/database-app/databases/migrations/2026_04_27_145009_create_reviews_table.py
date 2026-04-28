"""CreateReviewsTable Migration."""

from fastapi_startkit.masoniteorm.migrations import Migration


class CreateReviewsTable(Migration):
    async def up(self):
        """
        Run the migrations.
        """
        async with await self.schema.create("reviews") as table:
            table.increments("id")
            table.integer("reviewable_id").unsigned()
            table.string("reviewable_type")
            table.text("content")
            table.timestamps()

    async def down(self):
        """
        Revert the migrations.
        """
        await self.schema.drop("reviews")
