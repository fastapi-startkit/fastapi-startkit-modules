from pydantic.dataclasses import dataclass

@dataclass
class AIConfig:
    model: str = "gpt-3.5-turbo"
