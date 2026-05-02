from fastapi_startkit.carbon.carbon import Carbon
from fastapi_startkit.masoniteorm.models.fields import Field, DateTimeField
from fastapi_startkit.masoniteorm.relationships import (
    HasOne,
    BelongsTo,
    HasMany,
    HasManyThrough,
    BelongsToMany,
    HasOneThrough,
    MorphTo,
)
from fastapi_startkit.masoniteorm.models.model import Model


class User(Model):
    id: int
    name: str
    email: str
    email_verified_at: Carbon = DateTimeField(fmt="%Y-%m-%d %H:%M:%S", tz="UTC")
    is_admin: bool

    profile: "Profile" = HasOne("Profile", "user_id", "id")
    articles: "Articles" = HasMany("Articles", "id", "user_id")
    logos: "Logo" = HasManyThrough(
        ["Logo", "Articles"],
        "user_id",     # FK on Articles pointing to User
        "article_id",  # FK on Logo pointing to Articles
        "id",          # PK on User
        "id",          # PK on Logo
    )

    def get_is_admin(self) -> bool:
        return self.is_admin


class Profile(Model):
    __table__ = "profiles"
    __timestamps__ = False


class Logo(Model):
    __table__ = "logos"
    __timestamps__ = None

    published_date: Carbon = Field(json_schema_extra={"format": "YYYY-MM-DD HH:mm:ss"})


class Articles(Model):
    __table__ = "articles"
    __timestamps__ = None
    published_date: Carbon = Field(json_schema_extra={"format": "YYYY-MM-DD HH:mm:ss"})

    logo: "Logo" = BelongsTo("Logo", "id", "article_id")
    likes: "Like" = HasMany("Like", "id", "likeable_id")


class Store(Model):
    products: "Product" = BelongsToMany(
        "Product", "store_id", "product_id", "id", "id", with_timestamps=True
    )
    products_table: "Product" = BelongsToMany(
        "Product", "store_id", "product_id", "id", "id", table="product_table"
    )
    store_products: "Product" = BelongsToMany("Product")


class Product(Model):
    __table__ = "products"

    likes: "Like" = HasMany("Like", "id", "likeable_id")


class Like(Model):
    __table__ = "likes"

    record: "Model" = MorphTo("Like", "likeable_type", "likeable_id")


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


