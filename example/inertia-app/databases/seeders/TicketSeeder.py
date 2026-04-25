from app.models.Ticket import Ticket
from databases.factories.TicketFactory import ticket_factory


class TicketSeeder:
    async def run(self, count: int = 20):
        """Seed the tickets table with fake data."""
        for _ in range(count):
            await Ticket.create(ticket_factory())

        print(f"Seeded {count} tickets.")
