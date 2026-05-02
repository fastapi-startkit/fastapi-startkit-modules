from fastapi_startkit.carbon.carbon import Carbon
from fastapi_startkit.masoniteorm.models.fields import Field, DateTimeField
from fastapi_startkit.masoniteorm.relationships import (
    HasOne,
    BelongsTo,
    HasMany,
    BelongsToMany,
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
