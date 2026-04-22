import re


class Stringable:
    def __init__(self, text: str):
        self.text = text

    def __str__(self) -> str:
        return self.text

    def trim(self, suffix: str) -> 'Stringable':
        return Stringable(Str.trim(self.text, suffix))

    def slugify(self) -> 'Stringable':
        return Stringable(Str.slugify(self.text))


class Str:
    @classmethod
    def of(cls, text: str) -> 'Stringable':
        return Stringable(text)

    @classmethod
    def slugify(cls, text: str) -> str:
        """Strip all non-alphanumeric characters and lowercase."""
        return re.sub(r'[^a-z0-9]', '', text.lower())

    @classmethod
    def trim(cls, text: str, word: str) -> str:
        """Remove all occurrences of a word from the string (case-insensitive)."""
        return re.sub(re.escape(word), '', text, flags=re.IGNORECASE).strip('_').strip()
