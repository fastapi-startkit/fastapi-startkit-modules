import os
import pytest
from fastapi_startkit.config.app import AppConfig


class TestAppConfig:
    def test_default_name(self, monkeypatch):
        monkeypatch.delenv("APP_NAME", raising=False)
        assert AppConfig().name == "FastAPI starter kit"

    def test_custom_name(self, monkeypatch):
        monkeypatch.setenv("APP_NAME", "My App")
        assert AppConfig().name == "My App"

    def test_default_env(self, monkeypatch):
        monkeypatch.delenv("APP_ENV", raising=False)
        assert AppConfig().env == "development"

    def test_custom_env(self, monkeypatch):
        monkeypatch.setenv("APP_ENV", "production")
        assert AppConfig().env == "production"

    def test_default_debug_is_true(self, monkeypatch):
        monkeypatch.delenv("APP_DEBUG", raising=False)
        assert AppConfig().debug is True

    def test_debug_true_string(self, monkeypatch):
        monkeypatch.setenv("APP_DEBUG", "true")
        assert AppConfig().debug is True

    def test_debug_false_string(self, monkeypatch):
        monkeypatch.setenv("APP_DEBUG", "false")
        assert AppConfig().debug is False

    def test_debug_True_capitalised(self, monkeypatch):
        monkeypatch.setenv("APP_DEBUG", "True")
        assert AppConfig().debug is True

    def test_debug_False_capitalised(self, monkeypatch):
        monkeypatch.setenv("APP_DEBUG", "False")
        assert AppConfig().debug is False

    def test_default_timezone(self, monkeypatch):
        monkeypatch.delenv("APP_TIMEZONE", raising=False)
        assert AppConfig().timezone == "UTC"

    def test_custom_timezone(self, monkeypatch):
        monkeypatch.setenv("APP_TIMEZONE", "America/New_York")
        assert AppConfig().timezone == "America/New_York"

    def test_all_fields_set(self, monkeypatch):
        monkeypatch.setenv("APP_NAME", "Suite App")
        monkeypatch.setenv("APP_ENV", "testing")
        monkeypatch.setenv("APP_DEBUG", "false")
        monkeypatch.setenv("APP_TIMEZONE", "Europe/London")

        cfg = AppConfig()
        assert cfg.name == "Suite App"
        assert cfg.env == "testing"
        assert cfg.debug is False
        assert cfg.timezone == "Europe/London"
