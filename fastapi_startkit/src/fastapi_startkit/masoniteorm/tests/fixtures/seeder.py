from .model import User, Profile, Articles, Logo


async def seeder():
    user = await User.query().create({"email": "admin@admin.com", "name": "Joe", "is_admin": True})
    await Profile.create({"name": "Joe Profile", "user_id": user.id})
    article = await Articles.create(
        {"title": "Masonite ORM", "user_id": user.id, "published_date": "2020-01-01 00:00:00"}
    )
    await Logo.create({"article_id": article.id, "published_date": "2020-01-01 00:00:00"})
