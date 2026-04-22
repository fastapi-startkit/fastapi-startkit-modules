"""CreateTicketTagsTable Migration."""

from fastapi_startkit.masoniteorm.migrations import Migration


class CreateTicketTagsTable(Migration):
    async def up(self):
        """Run the migrations."""
        async with await self.schema.create("ticket_tags") as table:
            table.increments("id")

            table.unsigned_integer("ticket_id")
            table.foreign("ticket_id").references("id").on("tickets").on_delete("cascade")

            table.string("tag")  # e.g. Bug, Urgent, Question, Feature

    async def down(self):
        """Revert the migrations."""
        await self.schema.drop("ticket_tags")
