from cleo.application import Application
from masoniteorm.commands import (
    MigrateCommand,
    DBSeedCommand,
    MakeMigrationCommand,
)
from typer import Typer

app = Typer()
cleo = Application()

cleo.add(MakeMigrationCommand())
cleo.add(MigrateCommand())
cleo.add(DBSeedCommand())


@app.command()
def migrate():
    cleo.call("migrate")


@app.command()
def seed():
    cleo.call("db:seed", "DatabaseSeeder")


@app.command("make:migration")
def make(name: str):
    cleo.call("migration", name)
