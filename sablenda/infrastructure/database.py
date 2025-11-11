"""Database configuration and session management."""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


def get_database_path() -> Path:
    """Get the database file path in the application's roaming data directory.

    Returns the path to sablenda.db in %APPDATA%\\sablenda\\
    Creates the directory if it doesn't exist.

    """
    # Get the roaming app data directory
    appdata = os.environ.get('APPDATA')
    if not appdata:
        # Fallback to local directory if APPDATA is not available
        appdata = str(Path.home() / 'AppData' / 'Roaming')

    # Create sablenda directory
    sablenda_dir = Path(appdata) / 'sablenda'
    sablenda_dir.mkdir(parents=True, exist_ok=True)

    # Return the database file path
    return sablenda_dir / 'sablenda.db'


class DatabaseConfig:
    """Database configuration and session factory."""

    def __init__(self, database_path: Path | None = None):
        """Initialize database configuration.

        Args:
            database_path: Optional custom database path. If None, uses the default
                         app data roaming location.

        """
        if database_path is None:
            database_path = get_database_path()

        self.database_path = database_path
        self.engine = create_engine(
            f'sqlite:///{database_path}',
            echo=False,  # Set to True for SQL debugging
            connect_args={'check_same_thread': False}  # Allow multi-threaded access
        )
        self.SessionFactory = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        """Create and return a new database session."""
        return self.SessionFactory()

    def create_tables(self, metadata) -> None:
        """Create all tables defined in the metadata."""
        metadata.create_all(self.engine)
