"""Integration tests for MongoDB configuration utilities."""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_SRC = PROJECT_ROOT / "services" / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from core.config import Settings


def test_mongodb_url_validator_accepts_supported_schemes(monkeypatch):
    """Ensure MongoDB URLs with supported schemes are accepted and sanitized."""

    mongo_url = "mongodb://user:pass@mongo:27017/chonost"
    monkeypatch.setenv("MONGODB_URL", mongo_url)

    test_settings = Settings(_env_file=None)

    assert test_settings.get_mongodb_url() == mongo_url
    assert test_settings.get_sanitized_mongodb_url() == "mongodb://mongo:27017/chonost"


def test_mongodb_url_validator_rejects_unsupported_scheme(monkeypatch):
    """Reject MongoDB URLs that do not use the mongodb scheme."""

    monkeypatch.setenv("MONGODB_URL", "http://mongo:27017")

    with pytest.raises(ValueError):
        Settings(_env_file=None)
