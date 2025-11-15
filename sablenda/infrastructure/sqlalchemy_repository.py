"""SQLAlchemy implementation of the calendar repository.

This module provides the concrete implementation of ICalendarRepository using
SQLAlchemy for persistence to a SQLite database.

"""

from datetime import date, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from sablenda.data.models import Entry, RecurrenceType
from sablenda.domain.repository import ICalendarRepository
from sablenda.infrastructure.database import DatabaseConfig
from sablenda.infrastructure.schema import metadata


class SqlAlchemyCalendarRepository(ICalendarRepository):
    """SQLAlchemy implementation of the calendar repository."""

    def __init__(self, db_config: DatabaseConfig):
        """Initialize the repository with a database configuration.

        Args:
            db_config: Database configuration instance

        """
        self.db_config = db_config
        self.session: Session | None = None

        # Import mapping to ensure it's configured
        import sablenda.infrastructure.mapping

        # Create tables if they don't exist
        self.db_config.create_tables(metadata)

        # Create initial session
        self._ensure_session()

    def _ensure_session(self) -> None:
        """Ensure a database session is available."""
        if self.session is None or not self.session.is_active:
            self.session = self.db_config.get_session()

    def add(self, entry: Entry) -> None:
        """Add a new entry to the repository."""
        self._ensure_session()
        self.session.add(entry)

    def get_by_id(self, entry_id: UUID) -> Entry | None:
        """Retrieve an entry by its ID."""
        self._ensure_session()

        entry = self.session.query(Entry).filter(
            Entry.id == entry_id
        ).first()

        return entry

    def get_all(self) -> list[Entry]:
        """Retrieve all entries."""
        self._ensure_session()
        return self.session.query(Entry).all()

    def update(self, entry: Entry) -> bool:
        """Update an existing entry."""
        self._ensure_session()

        existing = self.get_by_id(entry.id)
        if existing is None:
            return False

        # Merge the updated entry into the session
        self.session.merge(entry)
        return True

    def remove(self, entry_id: UUID) -> bool:
        """Remove an entry by its ID."""
        self._ensure_session()

        entry = self.get_by_id(entry_id)
        if entry is None:
            return False

        self.session.delete(entry)
        return True

    def get_entries_for_date(self, check_date: date) -> list[Entry]:
        """Get all entries that occur on a specific date."""
        self._ensure_session()

        # Get all entries and filter using the domain logic
        all_entries = self.get_all()
        return [entry for entry in all_entries if entry.occurs_on(check_date)]

    def get_entries_for_date_range(self, start_date: date, end_date: date) -> dict[date, list[Entry]]:
        """Get all entries that occur within a date range, mapped by date."""
        self._ensure_session()

        # Initialize the result dictionary
        result: dict[date, list[Entry]] = {}

        # Get all entries once
        all_entries = self.get_all()

        # For each entry, determine which dates it occurs on within the range
        for entry in all_entries:
            # Iterate through each date in the range
            current_date = start_date
            while current_date <= end_date:
                if entry.occurs_on(current_date):
                    # Add this entry to the list for this date
                    if current_date not in result:
                        result[current_date] = []
                    result[current_date].append(entry)
                current_date += timedelta(days=1)

        return result

    def save_changes(self) -> None:
        """Persist any pending changes to the database."""
        self._ensure_session()

        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def close(self) -> None:
        """Close the database session."""
        if self.session is not None:
            self.session.close()
            self.session = None
