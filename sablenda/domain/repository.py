"""Repository interface for calendar entries following DDD pattern.

The repository interface is defined in the domain layer, while the implementation
is in the infrastructure layer. This ensures the domain remains independent of
persistence details.

"""

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from sablenda.data.models import Entry


class ICalendarRepository(ABC):
    """Interface for calendar entry repository."""

    @abstractmethod
    def add(self, entry: Entry) -> None:
        """Add a new entry to the repository.

        Args:
            entry: The entry to add

        """
        pass

    @abstractmethod
    def get_by_id(self, entry_id: UUID) -> Entry | None:
        """Retrieve an entry by its ID.

        Args:
            entry_id: The UUID of the entry

        Returns:
            The entry if found, None otherwise

        """
        pass

    @abstractmethod
    def get_all(self) -> list[Entry]:
        """Retrieve all entries.

        Returns:
            List of all entries in the repository

        """
        pass

    @abstractmethod
    def update(self, entry: Entry) -> bool:
        """Update an existing entry.

        Args:
            entry: The entry with updated data

        Returns:
            True if the entry was found and updated, False otherwise

        """
        pass

    @abstractmethod
    def remove(self, entry_id: UUID) -> bool:
        """Remove an entry by its ID.

        Args:
            entry_id: The UUID of the entry to remove

        Returns:
            True if the entry was found and removed, False otherwise

        """
        pass

    @abstractmethod
    def get_entries_for_date(self, check_date: date) -> list[Entry]:
        """Get all entries that occur on a specific date.

        Args:
            check_date: The date to check

        Returns:
            List of entries occurring on the given date

        """
        pass

    @abstractmethod
    def save_changes(self) -> None:
        """Persist any pending changes to the data store.

        This is typically called to commit a transaction or flush changes.

        """
        pass
