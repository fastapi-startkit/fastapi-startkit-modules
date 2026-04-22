from faker import Faker
import random

fake = Faker()

CHANNELS = ["email", "chat", "twitter", "phone", "web"]
PLANS = ["Free", "Starter", "Growth", "Enterprise"]
STATUSES = ["Open", "Waiting", "Closed", "Spam"]
TEAMS = ["Support", "Sales", "Billing", "Technical", "Onboarding"]

PREVIEWS = [
    "Hey, I'm having trouble logging in to my account...",
    "My payment failed and I need help resolving this immediately.",
    "Could you help me understand how to export my data?",
    "The dashboard is loading slowly since the last update.",
    "I'd like to upgrade my plan, can you walk me through it?",
    "There's an issue with the API returning 500 errors.",
    "Can I get a refund for last month's subscription?",
    "I accidentally deleted some important records, help!",
    "How do I add team members to my workspace?",
    "The email notifications stopped working for my account.",
]


def ticket_factory(overrides: dict = {}) -> dict:
    """Return a dict of fake ticket attributes."""
    return {
        "title": overrides.get("title", fake.sentence(nb_words=6).rstrip(".")),
        "team": overrides.get("team", random.choice(TEAMS)),
        "status": overrides.get("status", random.choice(STATUSES)),
        "from_name": overrides.get("from_name", fake.name()),
        "assignee_id": overrides.get("assignee_id", None),
        "preview": overrides.get("preview", random.choice(PREVIEWS)),
        "channel": overrides.get("channel", random.choice(CHANNELS)),
        "customer_since": overrides.get("customer_since", fake.date(pattern="%B %Y")),
        "plan": overrides.get("plan", random.choice(PLANS)),
        "monthly_sends": overrides.get(
            "monthly_sends", f"{random.randint(1, 500)}K"
        ),
        **{k: v for k, v in overrides.items() if k not in (
            "title", "team", "status", "from_name", "assignee_id",
            "preview", "channel", "customer_since", "plan", "monthly_sends",
        )},
    }
