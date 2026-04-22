"""CreateTicketMessagesTable Migration."""

from fastapi_startkit.masoniteorm.migrations import Migration


class CreateTicketMessagesTable(Migration):
    async def up(self):
        """Run the migrations."""
        async with await self.schema.create("ticket_messages") as table:
            table.increments("id")

            table.unsigned_integer("ticket_id")
            table.foreign("ticket_id").references("id").on("tickets").on_delete("cascade")

            # Can be a customer (no user account) or an agent (linked to users)
            table.unsigned_integer("user_id").nullable()
            table.foreign("user_id").references("id").on("users").nullable()

            table.string("author")        # display name
            table.string("avatar", 10).nullable()   # initials, e.g. "FV"
            table.text("body")
            table.boolean("is_reply").default(False)  # True = sent by an agent

            table.timestamps()

    async def down(self):
        """Revert the migrations."""
        await self.schema.drop("ticket_messages")
