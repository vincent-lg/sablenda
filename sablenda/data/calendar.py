"""Calendar data management."""

from datetime import date, timedelta
from uuid import UUID

from sablenda.data.models import Entry, FullDayEntry, TimedEvent
from sablenda.domain.repository import ICalendarRepository


class CalendarData:
    """Manages calendar entries using a repository for persistence."""

    def __init__(self, repository: ICalendarRepository | None = None):
        """
        Initialize the calendar with a repository.

        Args:
            repository: The repository to use for persistence.
                       If None, maintains in-memory list (legacy mode).
        """
        self.repository = repository
        self._entries_cache: list[Entry] | None = None
        # Cache for optimized month view: (start_date, end_date) -> dict[date, list[Entry]]
        self._date_range_cache: tuple[tuple[date, date], dict[date, list[Entry]]] | None = None

    @property
    def entries(self) -> list[Entry]:
        """Get all entries.

        This property is maintained for backward compatibility with existing code.
        If a repository is used, it fetches entries from the repository.
        Otherwise, it uses the in-memory cache.

        """
        if self.repository is not None:
            return self.repository.get_all()
        if self._entries_cache is None:
            self._entries_cache = []
        return self._entries_cache

    @entries.setter
    def entries(self, value: list[Entry]) -> None:
        """Set entries list (for backward compatibility with pickle loading).

        Args:
            value: List of entries to set

        """
        if self.repository is not None:
            # If using repository, clear and re-add all entries
            for entry in value:
                self.repository.add(entry)
            self.repository.save_changes()
        else:
            self._entries_cache = value

    def _invalidate_cache(self) -> None:
        """Invalidate the date range cache when entries are modified."""
        self._date_range_cache = None

    def add_entry(self, entry: Entry) -> None:
        """Add an entry to the calendar."""
        if self.repository is not None:
            self.repository.add(entry)
            self.repository.save_changes()
        else:
            if self._entries_cache is None:
                self._entries_cache = []
            self._entries_cache.append(entry)
        self._invalidate_cache()

    def remove_entry(self, entry_id: UUID) -> bool:
        """Remove an entry by ID. Returns True if found and removed."""
        if self.repository is not None:
            result = self.repository.remove(entry_id)
            if result:
                self.repository.save_changes()
                self._invalidate_cache()
            return result
        else:
            if self._entries_cache is None:
                return False
            for i, entry in enumerate(self._entries_cache):
                if entry.id == entry_id:
                    self._entries_cache.pop(i)
                    self._invalidate_cache()
                    return True
            return False

    def get_entry(self, entry_id: UUID) -> Entry | None:
        """Get an entry by ID."""
        if self.repository is not None:
            return self.repository.get_by_id(entry_id)
        else:
            if self._entries_cache is None:
                return None
            for entry in self._entries_cache:
                if entry.id == entry_id:
                    return entry
            return None

    def update_entry(self, entry: Entry) -> bool:
        """Update an existing entry. Returns True if found and updated."""
        if self.repository is not None:
            result = self.repository.update(entry)
            if result:
                self.repository.save_changes()
                self._invalidate_cache()
            return result
        else:
            if self._entries_cache is None:
                return False
            for i, existing in enumerate(self._entries_cache):
                if existing.id == entry.id:
                    self._entries_cache[i] = entry
                    self._invalidate_cache()
                    return True
            return False

    def get_entries_for_date(self, check_date: date) -> list[Entry]:
        """Get all entries that occur on the given date."""
        if self.repository is not None:
            return self.repository.get_entries_for_date(check_date)
        else:
            entries = self.entries
            return [entry for entry in entries if entry.occurs_on(check_date)]

    def has_entries_on_date(self, check_date: date) -> bool:
        """Check if there are any entries on the given date."""
        return len(self.get_entries_for_date(check_date)) > 0

    def get_entry_count_for_date(self, check_date: date) -> int:
        """Get the number of entries on the given date."""
        return len(self.get_entries_for_date(check_date))

    def get_month_days(self, year: int, month: int) -> list[date]:
        """Get all days to display for a month view.

        Returns a list of dates starting from the Monday of the week containing
        the first day of the month, and ending with the Sunday of the week
        containing the last day of the month.

        """
        # First day of the month
        first_day = date(year, month, 1)

        # Find the Monday of the week containing the first day
        # weekday() returns 0 for Monday, 6 for Sunday
        days_from_monday = first_day.weekday()
        start_date = first_day - timedelta(days=days_from_monday)

        # Last day of the month
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)

        # Find the Sunday of the week containing the last day
        days_to_sunday = 6 - last_day.weekday()
        end_date = last_day + timedelta(days=days_to_sunday)

        # Generate all dates from start to end
        current = start_date
        days = []
        while current <= end_date:
            days.append(current)
            current += timedelta(days=1)

        return days

    def get_entries_for_date_range(self, start_date: date, end_date: date) -> dict[date, list[Entry]]:
        """Get all entries that occur within a date range, mapped by date.

        This is an optimized batch operation that uses caching to avoid
        redundant calculations when viewing the same date range.

        Args:
            start_date: The start of the date range (inclusive)
            end_date: The end of the date range (inclusive)

        Returns:
            Dictionary mapping each date in the range to a list of entries
            occurring on that date. Dates with no entries will not be in the dict.

        """
        # Check if we have a cached result for this exact range
        if self._date_range_cache is not None:
            cached_range, cached_result = self._date_range_cache
            if cached_range == (start_date, end_date):
                return cached_result

        # Not in cache, compute the result
        if self.repository is not None:
            result = self.repository.get_entries_for_date_range(start_date, end_date)
        else:
            # Fallback for in-memory mode
            result: dict[date, list[Entry]] = {}
            entries = self.entries
            current_date = start_date
            while current_date <= end_date:
                entries_for_date = [entry for entry in entries if entry.occurs_on(current_date)]
                if entries_for_date:
                    result[current_date] = entries_for_date
                current_date += timedelta(days=1)

        # Cache the result
        self._date_range_cache = ((start_date, end_date), result)

        return result
