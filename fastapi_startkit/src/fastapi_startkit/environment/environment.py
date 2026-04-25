"""Module for the LoadEnvironment class."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


class LoadEnvironment:
    def __init__(self, environment=None, override=True, only=None, base_path=None):
        self.base_path = Path(base_path) if base_path else Path(".")
        self._detect_env_from_argv()

        if only:
            self._load(f".env.{only}", override=override)
            return

        resolved = self._resolve_environment(environment)

        # 2. Try .env.<resolved> first; fall back to .env when it doesn't exist.
        if resolved:
            specific = self.base_path / f".env.{resolved}"
            if specific.exists():
                load_dotenv(specific, override=override)
                return

        load_dotenv(self.base_path / ".env", override=override)

    def _detect_env_from_argv(self):
        """Parse --env=<value> or --env <value> from sys.argv, set APP_ENV,
        and remove the tokens so downstream CLI parsers (e.g. cleo) never see them."""
        args = sys.argv[1:]
        for i, arg in enumerate(args):
            if arg.startswith("--env="):
                os.environ["APP_ENV"] = arg.split("=", 1)[1]
                sys.argv.pop(i + 1)
                break
            if arg == "--env" and i + 1 < len(args):
                os.environ["APP_ENV"] = args[i + 1]
                sys.argv.pop(i + 2)  # value first (higher index)
                sys.argv.pop(i + 1)  # then the flag
                break

    def _resolve_environment(self, fallback):
        if "PYTEST_CURRENT_TEST" in os.environ:
            return "testing"

        if os.environ.get("APP_ENV"):
            return os.environ["APP_ENV"]

        if fallback:
            return fallback

        return None

    def _load(self, filename, override=False):
        path = self.base_path / filename
        load_dotenv(path, override=override)


def env(value, default="", cast=True):
    """Helper to retrieve the value of an environment variable or returns
    a default value. In addition, if type can be inferred then the value can be casted to the
    inferred type."""
    env_var = os.getenv(value, default)

    if not cast:
        return env_var

    if env_var == "":
        env_var = default

    if isinstance(env_var, bool):
        return env_var
    elif env_var is None:
        return None
    elif isinstance(env_var, int) or env_var.isnumeric():
        return int(env_var)
    elif env_var in ("false", "False"):
        return False
    elif env_var in ("true", "True"):
        return True
    else:
        return env_var
