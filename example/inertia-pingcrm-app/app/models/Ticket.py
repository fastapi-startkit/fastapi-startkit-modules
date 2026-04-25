from fastapi_startkit.masoniteorm.models import Model


class Ticket(Model):
    __table__ = "tickets"
    __primary_key__ = "id"

    id: int
    title: str
    team: str | None
    status: str
    from_name: str | None
    assignee_id: int | None
    preview: str | None
    channel: str | None
    customer_since: str | None
    plan: str | None
    monthly_sends: str | None
