"""CreateProfilesTable Migration."""

from fastapi_startkit.masoniteorm.migrations import Migration


class CreateProfilesTable(Migration):
    async def up(self):
        """
        Run the migrations.
        """
        async with await self.schema.create("profiles") as table:
            table.increments("id")
            table.integer("user_id").unsigned()
            table.foreign("user_id").references("id").on("users").on_delete("cascade")
            table.text("bio").nullable()
            table.string("country", length=100).nullable()
            table.string("phone_number", length=50).nullable()
            table.string("headline", length=255).nullable()
            table.text("description").nullable()
            table.string("video_url").nullable()
            table.integer("hourly_rate").nullable()
            table.json("languages_spoken").nullable()
            table.json("subjects").nullable()

            table.timestamps()

    async def down(self):
        """
        Revert the migrations.
        """
        await self.schema.drop("profiles")
