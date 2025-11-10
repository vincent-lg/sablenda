"""Data models for agenda entries."""
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from enum import Enum
from uuid import UUID, uuid4


class RecurrenceType(Enum):
    """Types of recurrence for entries."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class Entry:
    """Base class for calendar entries."""
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""
    entry_date: date = field(default_factory=date.today)
    recurrence: RecurrenceType = RecurrenceType.NONE

    def get_display_text(self) -> str:
        """Get the text to display for this entry."""
        return self.title if self.title else "Untitled"

    def occurs_on(self, check_date: date) -> bool:
        """Check if this entry occurs on the given date."""
        if check_date == self.entry_date:
            return True

        if self.recurrence == RecurrenceType.NONE:
            return False

        if check_date < self.entry_date:
            return False

        delta = (check_date - self.entry_date).days

        if self.recurrence == RecurrenceType.DAILY:
            return True
        elif self.recurrence == RecurrenceType.WEEKLY:
            return delta % 7 == 0
        elif self.recurrence == RecurrenceType.MONTHLY:
            # Occurs on the same day of each month
            return (check_date.day == self.entry_date.day and
                    check_date >= self.entry_date)
        elif self.recurrence == RecurrenceType.YEARLY:
            # Occurs on the same month and day each year
            return (check_date.month == self.entry_date.month and
                    check_date.day == self.entry_date.day and
                    check_date >= self.entry_date)

        return False


@dataclass
class FullDayEntry(Entry):
    """An all-day entry (birthday, holiday, reminder, etc.)."""
    pass


@dataclass
class TimedEvent(Entry):
    """An event with specific start and end times."""
    start_time: time = field(default_factory=lambda: time(9, 0))
    end_time: time = field(default_factory=lambda: time(10, 0))

    def get_display_text(self) -> str:
        """Get the text to display for this event including time."""
        title = super().get_display_text()
        return f"{self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')} {title}"
