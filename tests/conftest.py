# tests/conftest.py
import importlib
import pytest

@pytest.fixture(autouse=True)
def fresh_helpers_module(monkeypatch):
    """
    Reload app.helpers to ensure a clean module state for each test,
    and reset the module-level _seq_counter used by emit_funds_update.
    """
    import app.helpers as helpers
    importlib.reload(helpers)
    helpers._seq_counter = 0  # type: ignore[attr-defined]
    return helpers

