import asyncio

from dumpdie import dd

from bootstrap.application import app

from app.models.Organization import Organization


async def index():
    paginator = await (
        Organization.query()
        .paginate()
    )

    dd(paginator)


if __name__ == "__main__":
    asyncio.run(index())
