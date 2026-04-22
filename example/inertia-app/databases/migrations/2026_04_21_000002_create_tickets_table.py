"""CreateTicketsTable Migration."""

from fastapi_startkit.masoniteorm.migrations import Migration


class CreateTicketsTable(Migration):
    async def up(self):
        """Run the migrations."""
        async with await self.schema.create("tickets") as table:
            table.increments("id")

            table.string("title")
            table.string("team").nullable()

            # status: Open | Waiting | Closed | Spam
            table.enum("status", ["Open", "Waiting", "Closed", "Spam"]).default("Open")

            # Sender / assignee
            table.string("from_name").nullable()
            table.unsigned_integer("assignee_id").nullable()
            table.foreign("assignee_id").references("id").on("users").nullable()

            # Display metadata shown in the ticket list / detail
            table.text("preview").nullable()
            table.string("channel").nullable()

            # Customer info displayed in the meta-panel
            table.string("customer_since").nullable()
            table.string("plan").nullable()
            table.string("monthly_sends").nullable()

            table.timestamps()

    async def down(self):
        """Revert the migrations."""
        await self.schema.drop("tickets")
