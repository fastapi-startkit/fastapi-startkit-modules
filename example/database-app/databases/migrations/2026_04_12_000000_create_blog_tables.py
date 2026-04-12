from fastapi_startkit.masoniteorm.migrations import Migration

class CreateBlogTables(Migration):
    async def up(self):
        """
        Run the migrations.
        """
        # Users Table
        async with await self.schema.create("users") as table:
            table.increments("id")
            table.string("name")
            table.string("email").unique()
            table.string("password")
            table.timestamps()

        # Posts Table
        async with await self.schema.create("posts") as table:
            table.increments("id")
            table.integer("user_id").unsigned()
            table.foreign("user_id").references("id").on("users")
            table.string("title")
            table.text("content")
            table.timestamps()

        # Tags Table
        async with await self.schema.create("tags") as table:
            table.increments("id")
            table.string("name").unique()
            table.timestamps()

        # Post-Tag Pivot Table
        async with await self.schema.create("post_tag") as table:
            table.increments("id")
            table.integer("post_id").unsigned()
            table.foreign("post_id").references("id").on("posts").on_delete("cascade")
            table.integer("tag_id").unsigned()
            table.foreign("tag_id").references("id").on("tags").on_delete("cascade")

        # Media Table
        async with await self.schema.create("media") as table:
            table.increments("id")
            table.integer("post_id").unsigned()
            table.foreign("post_id").references("id").on("posts").on_delete("cascade")
            table.string("url")
            table.timestamps()

    async def down(self):
        """
        Revert the migrations.
        """
        await self.schema.drop("media")
        await self.schema.drop("post_tag")
        await self.schema.drop("tags")
        await self.schema.drop("posts")
        await self.schema.drop("users")
