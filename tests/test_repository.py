"""Tests for the SQLAlchemy repository implementation."""

from datetime import date, time
from uuid import uuid4

import pytest

from sablenda.data.models import Entry, FullDayEntry, TimedEvent, RecurrenceType
from sablenda.infrastructure.sqlalchemy_repository import SqlAlchemyCalendarRepository


@pytest.fixture
def repository(db_config):
    """Create a repository instance for testing."""
    repo = SqlAlchemyCalendarRepository(db_config)
    yield repo
    repo.close()
    # Dispose of the engine to close all connections
    db_config.engine.dispose()


def test_add_full_day_entry(repository):
    """Test adding a full day entry to the repository."""
    entry = FullDayEntry(
        title="Birthday",
        description="John's birthday",
        entry_date=date(2025, 5, 15),
        recurrence=RecurrenceType.YEARLY
    )

    repository.add(entry)
    repository.save_changes()

    # Retrieve and verify
    retrieved = repository.get_by_id(entry.id)
    assert retrieved is not None
    assert isinstance(retrieved, FullDayEntry)
    assert retrieved.title == "Birthday"
    assert retrieved.description == "John's birthday"
    assert retrieved.entry_date == date(2025, 5, 15)
    assert retrieved.recurrence == RecurrenceType.YEARLY


def test_add_timed_event(repository):
    """Test adding a timed event to the repository."""
    entry = TimedEvent(
        title="Team Meeting",
        description="Weekly standup",
        entry_date=date(2025, 11, 15),
        start_time=time(10, 0),
        end_time=time(11, 0),
        recurrence=RecurrenceType.WEEKLY
    )

    repository.add(entry)
    repository.save_changes()

    # Retrieve and verify
    retrieved = repository.get_by_id(entry.id)
    assert retrieved is not None
    assert isinstance(retrieved, TimedEvent)
    assert retrieved.title == "Team Meeting"
    assert retrieved.start_time == time(10, 0)
    assert retrieved.end_time == time(11, 0)
    assert retrieved.recurrence == RecurrenceType.WEEKLY


def test_get_by_id_nonexistent(repository):
    """Test retrieving a non-existent entry returns None."""
    fake_id = uuid4()
    result = repository.get_by_id(fake_id)
    assert result is None


def test_get_all_empty(repository):
    """Test get_all on empty repository returns empty list."""
    result = repository.get_all()
    assert result == []


def test_get_all_multiple_entries(repository):
    """Test get_all returns all entries."""
    entry1 = FullDayEntry(title="Event 1", entry_date=date(2025, 1, 1))
    entry2 = TimedEvent(
        title="Event 2",
        entry_date=date(2025, 1, 2),
        start_time=time(9, 0),
        end_time=time(10, 0)
    )
    entry3 = FullDayEntry(title="Event 3", entry_date=date(2025, 1, 3))

    repository.add(entry1)
    repository.add(entry2)
    repository.add(entry3)
    repository.save_changes()

    all_entries = repository.get_all()
    assert len(all_entries) == 3


def test_update_entry(repository):
    """Test updating an existing entry."""
    entry = FullDayEntry(
        title="Original Title",
        description="Original Description",
        entry_date=date(2025, 5, 15)
    )

    repository.add(entry)
    repository.save_changes()

    # Modify the entry
    entry.title = "Updated Title"
    entry.description = "Updated Description"

    result = repository.update(entry)
    repository.save_changes()

    assert result is True

    # Verify the update
    retrieved = repository.get_by_id(entry.id)
    assert retrieved.title == "Updated Title"
    assert retrieved.description == "Updated Description"


def test_update_nonexistent_entry(repository):
    """Test updating a non-existent entry returns False."""
    entry = FullDayEntry(
        id=uuid4(),
        title="Non-existent",
        entry_date=date(2025, 1, 1)
    )

    result = repository.update(entry)
    assert result is False


def test_remove_entry(repository):
    """Test removing an entry."""
    entry = FullDayEntry(title="To Remove", entry_date=date(2025, 1, 1))

    repository.add(entry)
    repository.save_changes()

    # Remove the entry
    result = repository.remove(entry.id)
    repository.save_changes()

    assert result is True

    # Verify it's gone
    retrieved = repository.get_by_id(entry.id)
    assert retrieved is None


def test_remove_nonexistent_entry(repository):
    """Test removing a non-existent entry returns False."""
    fake_id = uuid4()
    result = repository.remove(fake_id)
    assert result is False


def test_get_entries_for_date_no_entries(repository):
    """Test getting entries for a date with no entries."""
    result = repository.get_entries_for_date(date(2025, 1, 1))
    assert result == []


def test_get_entries_for_date_single_entry(repository):
    """Test getting entries for a specific date."""
    entry = FullDayEntry(title="Test Event", entry_date=date(2025, 5, 15))

    repository.add(entry)
    repository.save_changes()

    # Should find the entry on the correct date
    result = repository.get_entries_for_date(date(2025, 5, 15))
    assert len(result) == 1
    assert result[0].title == "Test Event"

    # Should not find it on a different date
    result = repository.get_entries_for_date(date(2025, 5, 16))
    assert len(result) == 0


def test_get_entries_for_date_with_recurrence(repository):
    """Test getting recurring entries for various dates."""
    # Weekly recurring event starting May 15, 2025 (Thursday)
    entry = FullDayEntry(
        title="Weekly Meeting",
        entry_date=date(2025, 5, 15),
        recurrence=RecurrenceType.WEEKLY
    )

    repository.add(entry)
    repository.save_changes()

    # Should appear on the original date
    result = repository.get_entries_for_date(date(2025, 5, 15))
    assert len(result) == 1

    # Should appear one week later
    result = repository.get_entries_for_date(date(2025, 5, 22))
    assert len(result) == 1

    # Should NOT appear one day later
    result = repository.get_entries_for_date(date(2025, 5, 16))
    assert len(result) == 0


def test_get_entries_for_date_multiple_entries(repository):
    """Test getting multiple entries on the same date."""
    entry1 = FullDayEntry(title="Event 1", entry_date=date(2025, 5, 15))
    entry2 = TimedEvent(
        title="Event 2",
        entry_date=date(2025, 5, 15),
        start_time=time(9, 0),
        end_time=time(10, 0)
    )
    entry3 = FullDayEntry(title="Event 3", entry_date=date(2025, 5, 16))

    repository.add(entry1)
    repository.add(entry2)
    repository.add(entry3)
    repository.save_changes()

    # Should get 2 entries for May 15
    result = repository.get_entries_for_date(date(2025, 5, 15))
    assert len(result) == 2

    # Should get 1 entry for May 16
    result = repository.get_entries_for_date(date(2025, 5, 16))
    assert len(result) == 1


def test_persistence_across_sessions(db_config):
    """Test that data persists across repository sessions."""
    # Create a repository and add an entry
    repo1 = SqlAlchemyCalendarRepository(db_config)
    entry = FullDayEntry(title="Persistent Event", entry_date=date(2025, 1, 1))
    entry_id = entry.id

    repo1.add(entry)
    repo1.save_changes()
    repo1.close()
    db_config.engine.dispose()

    # Create a new repository instance and verify the entry persists
    repo2 = SqlAlchemyCalendarRepository(db_config)
    retrieved = repo2.get_by_id(entry_id)

    assert retrieved is not None
    assert retrieved.title == "Persistent Event"
    assert retrieved.entry_date == date(2025, 1, 1)

    repo2.close()
    db_config.engine.dispose()


def test_rollback_on_error(repository):
    """Test that changes are rolled back on error."""
    entry = FullDayEntry(title="Test Event", entry_date=date(2025, 1, 1))
    repository.add(entry)

    # Don't save changes, close the session
    repository.close()

    # Recreate the session and verify the entry wasn't saved
    repository._ensure_session()
    result = repository.get_by_id(entry.id)
    assert result is None
