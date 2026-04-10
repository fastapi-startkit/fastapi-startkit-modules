from fastapi_startkits.providers import Provider


class DatabaseProvider(Provider):
    def register(self):
        config = self.app.make("config")

        from masoniteorm.query import QueryBuilder
        from masoniteorm.connections import ConnectionResolver

        # Register ConnectionResolver
        db_config = config.get("database.databases") or config.get("database")
        resolver = ConnectionResolver().set_connection_details(db_config)
        self.app.bind("resolver", resolver)

        # Register QueryBuilder
        self.app.bind(
            "builder",
            QueryBuilder(connection_details=db_config, connection='default'),
        )

        # Register Migrations and Seeds locations
        self.app.bind("migrations.location", "databases/migrations")
        self.app.bind("seeds.location", "databases/seeds")

    def boot(self):
        pass
