"""Tests for database infrastructure."""

from pathlib import Path

from sablenda.infrastructure.database import DatabaseConfig, get_database_path


def test_get_database_path_creates_directory(tmp_path, monkeypatch):
    """Test that get_database_path creates the sablenda directory."""
    # Mock APPDATA to use a temporary directory
    fake_appdata = tmp_path / "AppData" / "Roaming"
    monkeypatch.setenv("APPDATA", str(fake_appdata))

    db_path = get_database_path()

    # Check that the path is correct
    assert db_path == fake_appdata / "sablenda" / "sablenda.db"
    # Check that the directory was created
    assert db_path.parent.exists()
    assert db_path.parent.is_dir()


def test_database_config_initialization(temp_db_path):
    """Test that DatabaseConfig initializes correctly."""
    config = DatabaseConfig(database_path=temp_db_path)

    assert config.database_path == temp_db_path
    assert config.engine is not None
    assert config.SessionFactory is not None


def test_database_config_get_session(db_config):
    """Test that get_session creates a valid session."""
    session = db_config.get_session()

    assert session is not None
    assert session.is_active

    session.close()


def test_database_config_creates_tables(db_config):
    """Test that create_tables creates the database schema."""
    from sqlalchemy import text
    from sablenda.infrastructure.schema import metadata

    # Create tables
    db_config.create_tables(metadata)

    # Verify the database file was created
    assert db_config.database_path.exists()

    # Verify tables exist by checking metadata
    session = db_config.get_session()
    try:
        # Query the sqlite_master table to check if our table exists
        result = session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='entries'")
        )
        tables = [row[0] for row in result]
        assert 'entries' in tables
    finally:
        session.close()
        # Dispose of the engine to close all connections
        db_config.engine.dispose()


def test_database_config_uses_default_path_when_none():
    """Test that DatabaseConfig uses default path when none provided."""
    config = DatabaseConfig()

    # Should use the default app data path
    assert config.database_path is not None
    assert config.database_path.name == "sablenda.db"
