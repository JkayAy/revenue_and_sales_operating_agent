import pytest
from sales_api.config import settings


@pytest.fixture(autouse=True)
def force_memory_store(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit tests use in-memory store unless INTEGRATION_DB is set."""
    if not __import__("os").environ.get("INTEGRATION_DB"):
        monkeypatch.setenv("DATABASE_URL", "")
        monkeypatch.setattr(settings, "database_url", "")
