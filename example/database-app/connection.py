import asyncio
import os

from fastapi_startkit.masoniteorm.connections.manager import DBManager

# Configuration
DATABASES = {
    "default": "postgres",
    "postgres": {
        "driver": "postgres",
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "database": os.getenv("DB_DATABASE", "local"),
        "user": os.getenv("DB_USERNAME", "local"),
        "password": os.getenv("DB_PASSWORD", "secret"),
        "port": os.getenv("DB_PORT", "5432"),
        "prefix": "",
        "options": {
            "min_size": 1,
            "max_size": 10,
        },
    },
    "sqlite": {
        "driver": "sqlite",
        "database": "database.sqlite",
    }
}

DB = DBManager(connection_details=DATABASES)

async def test_connection():
    try:
        # Test Postgres
        pg_connection = DB.connection("postgres")
        print("Connecting to Postgres (Async)...")
        res_pg = await pg_connection.query("SELECT 1 as connected")
        print(f"Postgres Result: {res_pg}")

        # Test Isolation
        sqlite_connection = DB.connection("sqlite")
        print("Connecting to SQLite (Async)...")
        res_sqlite = await sqlite_connection.query("SELECT 1 as connected")
        print(f"SQLite Result: {res_sqlite}")

        # Test Transaction Helper
        print("Testing Transaction Helper...")
        await DB.begin_transaction("sqlite")
        await sqlite_connection.query("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
        await DB.commit_transaction("sqlite")
        print("Transaction Successful")

        # Test Transaction Context Manager
        print("Testing Transaction Context Manager...")
        async with DB.transaction("sqlite") as conn:
            await conn.query("INSERT INTO test (id) VALUES (1)")
        print("Context Manager Transaction Successful")

    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())

