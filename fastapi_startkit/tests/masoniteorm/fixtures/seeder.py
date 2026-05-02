from .model import User, Profile, Articles, Logo, Country, Port, IncomingShipment


async def seeder():
    user = await User.query().create(
        {"email": "admin@admin.com", "name": "Joe", "is_admin": True}
    )
    await Profile.create({"name": "Joe Profile", "user_id": user.id})
    article = await Articles.create(
        {
            "title": "Masonite ORM",
            "user_id": user.id,
            "published_date": "2020-01-01 00:00:00",
        }
    )
    await Logo.create(
        {"article_id": article.id, "published_date": "2020-01-01 00:00:00"}
    )

    await Country.query().insert(
        [
            {"country_id": 10, "name": "Australia"},
            {"country_id": 20, "name": "USA"},
            {"country_id": 30, "name": "Canada"},
            {"country_id": 40, "name": "United Kingdom"},
        ]
    )

    await Port.query().insert(
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

    await IncomingShipment.query().insert(
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
