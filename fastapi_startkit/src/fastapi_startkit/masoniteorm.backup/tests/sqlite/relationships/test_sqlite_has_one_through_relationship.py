import pytest_asyncio

from fastapi_startkit.masoniteorm.connections.sqlite_connection import SQLiteConnection
from fastapi_startkit.masoniteorm.models import Model
from fastapi_startkit.masoniteorm.relationships import HasOneThrough
from fastapi_startkit.masoniteorm.schema import Schema
from fastapi_startkit.masoniteorm.schema.platforms import SQLitePlatform


class Port(Model):
    __table__ = "ports"
    __connection__ = "dev"


class Country(Model):
    __table__ = "countries"
    __connection__ = "dev"


class IncomingShipment(Model):
    __table__ = "incoming_shipments"
    __connection__ = "dev"

    from_country: "Country" = HasOneThrough(
        ["Country", "Port"],
        "from_port_id",  # FK on IncomingShipment → Port
        "port_country_id",  # FK on Port → Country
        "port_id",  # PK on Port
        "country_id",  # PK on Country
    )


class TestHasOneThroughRelationship:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        # Reset shared engine cache so each test class gets a fresh in-memory DB.
        SQLiteConnection._shared_engines.clear()

        self.schema = Schema(
            connection="dev",
            platform=SQLitePlatform,
            config_path="fastapi_startkit/masoniteorm/tests/integrations/config/database",
        ).on("dev")

        async with await self.schema.create_table_if_not_exists(
            "incoming_shipments"
        ) as table:
            table.integer("shipment_id").primary()
            table.string("name")
            table.integer("from_port_id")

        async with await self.schema.create_table_if_not_exists("ports") as table:
            table.integer("port_id").primary()
            table.string("name")
            table.integer("port_country_id")

        async with await self.schema.create_table_if_not_exists("countries") as table:
            table.integer("country_id").primary()
            table.string("name")

        await (
            Country()
            .get_builder()
            .bulk_create(
                [
                    {"country_id": 10, "name": "Australia"},
                    {"country_id": 20, "name": "USA"},
                    {"country_id": 30, "name": "Canada"},
                    {"country_id": 40, "name": "United Kingdom"},
                ]
            )
        )

        await (
            Port()
            .get_builder()
            .bulk_create(
                [
                    {"port_id": 100, "name": "Melbourne", "port_country_id": 10},
                    {"port_id": 200, "name": "Darwin", "port_country_id": 10},
                    {"port_id": 300, "name": "South Louisiana", "port_country_id": 20},
                    {"port_id": 400, "name": "Houston", "port_country_id": 20},
                    {"port_id": 500, "name": "Montreal", "port_country_id": 30},
                    {"port_id": 600, "name": "Vancouver", "port_country_id": 30},
                    {"port_id": 700, "name": "Southampton", "port_country_id": 40},
                    {"port_id": 800, "name": "London Gateway", "port_country_id": 40},
                ]
            )
        )

        await (
            IncomingShipment()
            .get_builder()
            .bulk_create(
                [
                    {"name": "Bread", "from_port_id": 300},
                    {"name": "Milk", "from_port_id": 100},
                    {"name": "Tractor Parts", "from_port_id": 100},
                    {"name": "Fridges", "from_port_id": 700},
                    {"name": "Wheat", "from_port_id": 600},
                    {"name": "Kettles", "from_port_id": 400},
                    {"name": "Bread", "from_port_id": 700},
                ]
            )
        )

        yield

        await self.schema.drop_table_if_exists("incoming_shipments")
        await self.schema.drop_table_if_exists("ports")
        await self.schema.drop_table_if_exists("countries")
        SQLiteConnection._shared_engines.clear()

    async def test_has_one_through_can_eager_load(self):
        shipments = await (
            IncomingShipment.where("name", "Bread").with_("from_country").get()
        )
        assert shipments.count() == 2

        shipment1 = shipments.shift()
        assert isinstance(shipment1.from_country, Country)
        assert shipment1.from_country.country_id == 20

        shipment2 = shipments.shift()
        assert isinstance(shipment2.from_country, Country)
        assert shipment2.from_country.country_id == 40

        # check .first() and .get() produce the same result
        single = await (
            IncomingShipment.where("name", "Tractor Parts")
            .with_("from_country")
            .first()
        )
        single_get = await (
            IncomingShipment.where("name", "Tractor Parts").with_("from_country").get()
        )
        assert single.from_country.country_id == 10
        assert single_get.count() == 1
        assert (
            single.from_country.country_id == single_get.first().from_country.country_id
        )

    async def test_has_one_through_eager_load_can_be_empty(self):
        shipments = await (
            IncomingShipment.where("name", "Bread")
            .where_has("from_country", lambda query: query.where("name", "Uruguay"))
            .with_("from_country")
            .get()
        )
        assert shipments.count() == 0

    async def test_has_one_through_can_get_related(self):
        shipment = await IncomingShipment.where("name", "Milk").first()
        country = await shipment.from_country
        assert isinstance(country, Country)
        assert country.country_id == 10

    async def test_has_one_through_has_query(self):
        shipments = await IncomingShipment.where_has(
            "from_country", lambda query: query.where("name", "USA")
        ).get()
        assert shipments.count() == 2
