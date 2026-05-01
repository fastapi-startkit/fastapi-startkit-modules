from .db import DB

schema = DB.get_schema_builder()


async def wipe():
    tables = await schema.on("default").get_all_tables()
    for table in tables:
        await schema.on("default").drop_table_if_exists(table)


async def migrate():
    async with await schema.on("default").create_table_if_not_exists("users") as table:
        table.id()
        table.string("name")
        table.string("email").unique()
        table.boolean("is_admin").default(False)
        table.timestamp("email_verified_at").nullable()
        table.timestamps()

    async with await schema.create_table_if_not_exists("profiles") as table:
        table.integer("id").primary()
        table.string("name")
        table.integer("user_id")

    async with await schema.create_table_if_not_exists("articles") as table:
        table.id()
        table.string("title")
        table.integer("user_id")
        table.datetime("published_date")

    async with await schema.create_table_if_not_exists("logos") as table:
        table.id()
        table.integer("article_id")
        table.datetime("published_date")

    async with await schema.create_table_if_not_exists("users") as table:
        table.id()
        table.string("name")
        table.boolean("is_admin").default(False)
        table.datetime("created_at")
        table.datetime("updated_at")

    async with await schema.create_table_if_not_exists("stores") as table:
        table.integer("id").primary()
        table.string("name")

    async with await schema.create_table_if_not_exists("products") as table:
        table.id()
        table.string("name")
        table.timestamps()

    async with await schema.create_table_if_not_exists("product_table") as table:
        table.id()
        table.integer("store_id")
        table.integer("product_id")

    async with await schema.create_table_if_not_exists("product_store") as table:
        table.id()
        table.integer("store_id")
        table.integer("product_id")
        table.timestamps()
