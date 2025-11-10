"""Pickle-based storage for the agenda."""
import pickle
from pathlib import Path

from agenda.data.calendar import CalendarData


class PickleStorage:
    """Storage implementation using pickle."""

    def __init__(self, file_path: str | Path = "agenda_data.pkl"):
        """Initialize the storage with a file path."""
        self.file_path = Path(file_path)

    def save(self, calendar: CalendarData) -> None:
        """Save the calendar data to disk."""
        with open(self.file_path, 'wb') as f:
            pickle.dump(calendar.entries, f)

    def load(self) -> CalendarData:
        """Load the calendar data from disk."""
        calendar = CalendarData()

        if self.file_path.exists():
            with open(self.file_path, 'rb') as f:
                calendar.entries = pickle.load(f)

        return calendar
