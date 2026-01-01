"""
Environment variable utilities.
"""
import os


def env_bool(name: str, default: bool) -> bool:
    """Return a boolean environment variable with a safe fallback."""
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.lower() in {"1", "true", "yes", "on"}
