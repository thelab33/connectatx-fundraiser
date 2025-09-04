# tests/conftest.py
# --- ensure project root is importable as a package ---
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# ------------------------------------------------------

import importlib
# (rest of your file — the fixture that imports app.helpers, etc.)

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

