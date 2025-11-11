"""Pytest configuration and shared fixtures."""

import tempfile
from pathlib import Path

import pytest

from sablenda.infrastructure.database import DatabaseConfig


@pytest.fixture
def temp_db_path():
    """Create a temporary database file path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_sablenda.db"
        yield db_path


@pytest.fixture
def db_config(temp_db_path):
    """Create a database configuration with a temporary database."""
    return DatabaseConfig(database_path=temp_db_path)
