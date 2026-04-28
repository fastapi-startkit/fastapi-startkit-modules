import pytest
from httpx import AsyncClient, ASGITransport
from bootstrap.application import app
from fastapi_startkit.masoniteorm.migrations import Migration


@pytest.fixture(scope="class")
async def refresh_database():
    migration = Migration(migration_directory="databases/migrations")
    await migration.fresh(ignore_fk=True)
    yield


@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app.fastapi), base_url="http://test") as client:
        yield client