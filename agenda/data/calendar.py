"""Calendar data management."""
from datetime import date, timedelta
from uuid import UUID

from agenda.data.models import Entry, FullDayEntry, TimedEvent


class CalendarData:
    """Manages calendar entries."""

    def __init__(self):
        """Initialize an empty calendar."""
        self.entries: list[Entry] = []

    def add_entry(self, entry: Entry) -> None:
        """Add an entry to the calendar."""
        self.entries.append(entry)

    def remove_entry(self, entry_id: UUID) -> bool:
        """Remove an entry by ID. Returns True if found and removed."""
        for i, entry in enumerate(self.entries):
            if entry.id == entry_id:
                self.entries.pop(i)
                return True
        return False

    def get_entry(self, entry_id: UUID) -> Entry | None:
        """Get an entry by ID."""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

    def update_entry(self, entry: Entry) -> bool:
        """Update an existing entry. Returns True if found and updated."""
        for i, existing in enumerate(self.entries):
            if existing.id == entry.id:
                self.entries[i] = entry
                return True
        return False

    def get_entries_for_date(self, check_date: date) -> list[Entry]:
        """Get all entries that occur on the given date."""
        return [entry for entry in self.entries if entry.occurs_on(check_date)]

    def has_entries_on_date(self, check_date: date) -> bool:
        """Check if there are any entries on the given date."""
        return len(self.get_entries_for_date(check_date)) > 0

    def get_entry_count_for_date(self, check_date: date) -> int:
        """Get the number of entries on the given date."""
        return len(self.get_entries_for_date(check_date))

    def get_month_days(self, year: int, month: int) -> list[date]:
        """
        Get all days to display for a month view.

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
