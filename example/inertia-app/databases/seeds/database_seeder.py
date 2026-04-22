from databases.seeders.TicketSeeder import TicketSeeder


class DatabaseSeeder:
    async def run(self):
        await TicketSeeder(connection=self.connection).run()
