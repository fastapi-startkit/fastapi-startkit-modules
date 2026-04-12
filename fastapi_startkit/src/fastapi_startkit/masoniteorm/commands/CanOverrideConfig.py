from cleo.commands.command import Command
from cleo.helpers import option


class CanOverrideConfig(Command):
    def configure(self):
        super().configure()
        self.definition.add_option(
            option(
                "config",
                "C",
                description="The path to the ORM configuration file. If not given DB_CONFIG_PATH env variable will be used and finally 'config.database'.",
                flag=False,
                value_required=True,
            )
        )
