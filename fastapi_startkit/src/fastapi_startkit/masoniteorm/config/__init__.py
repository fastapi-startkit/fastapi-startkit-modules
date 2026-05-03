import os
from urllib.parse import urlparse


def db_url(url: str = None, log_queries: bool = False, prefix: str = "", options: dict = None) -> dict:
    """Parse a database URL string into a connection config dict."""
    if url is None:
        url = os.environ.get("DATABASE_URL")
        if not url:
            raise ValueError("No DATABASE_URL environment variable set")

    parsed = urlparse(url)
    scheme = parsed.scheme  # e.g. "mysql", "sqlite", "postgres", "postgresql", "mssql"

    # Normalize driver name
    driver = scheme.replace("postgresql", "postgres")

    config = {
        "driver": driver,
        "database": parsed.path.lstrip("/") or ":memory:",
        "prefix": prefix,
        "options": options or {},
        "log_queries": log_queries,
    }

    if driver == "sqlite":
        db = parsed.netloc + parsed.path
        if not db or db == "/:memory:":
            db = ":memory:"
        else:
            db = db.lstrip("/")
        config["database"] = db
        return config

    config["user"] = parsed.username or ""
    config["password"] = parsed.password or ""
    config["host"] = parsed.hostname or "localhost"

    port = parsed.port
    if port is not None:
        if driver in ("mysql",):
            config["port"] = int(port)
        else:
            config["port"] = port

    return config
