"""Keep the tracked local development database untouched during tests."""

import os
import shutil
import tempfile
from pathlib import Path

import pytest


_BACKEND_DIR = Path(__file__).resolve().parents[1]
_TEST_DIR = Path(tempfile.mkdtemp(prefix="alterlife-tests-"))
_TEST_DB = _TEST_DIR / "alterlife_db.json"
shutil.copy2(_BACKEND_DIR / "alterlife_db.json", _TEST_DB)
os.environ["ALTERLIFE_DB_FILE"] = str(_TEST_DB)
os.environ.setdefault("ENVIRONMENT", "test")


@pytest.fixture(scope="session", autouse=True)
def isolated_database():
    yield
    shutil.rmtree(_TEST_DIR, ignore_errors=True)
