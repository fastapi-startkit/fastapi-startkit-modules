from typing import Any


class Config:
    """Configuration facades to manage Masonite config files."""
    @staticmethod
    def get(key: str, default: str | None = None) -> Any:
        """Get a given key in config, can use a dotted path."""
        ...

    @staticmethod
    def set(key: str, value: Any) -> None:
        """Override config for a given key."""
        ...

    def all(self) -> dict:
        """Get all config object."""
        ...
