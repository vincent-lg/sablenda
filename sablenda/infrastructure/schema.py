"""Database schema definitions using SQLAlchemy Core.

This module defines the database schema separately from the domain models,
following the classical mapping pattern.

"""

from uuid import UUID

from sqlalchemy import (
    Column,
    Date,
    Integer,
    MetaData,
    String,
    Table,
    Time,
    TypeDecorator,
)

from sablenda.data.models import RecurrenceType


class UUIDType(TypeDecorator):
    """Custom type for storing UUID as string."""

    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert UUID to string when storing."""
        if value is None:
            return value
        if isinstance(value, UUID):
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        """Convert string to UUID when loading."""
        if value is None:
            return value
        if isinstance(value, str):
            return UUID(value)
        return value


class RecurrenceTypeType(TypeDecorator):
    """Custom type for storing RecurrenceType enum as string."""

    impl = String(20)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert RecurrenceType to string when storing."""
        if value is None:
            return 'none'
        if isinstance(value, RecurrenceType):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        """Convert string to RecurrenceType when loading."""
        if value is None:
            return RecurrenceType.NONE
        if isinstance(value, str):
            return RecurrenceType(value)
        return value


# Create metadata object
metadata = MetaData()

# Entries table - stores all entry types with single table inheritance
entries_table = Table(
    'entries',
    metadata,
    Column('id', UUIDType, primary_key=True),  # UUID with custom type converter
    Column('entry_type', String(50), nullable=False),  # Discriminator column
    Column('title', String(255), nullable=False, default=''),
    Column('description', String, nullable=False, default=''),
    Column('entry_date', Date, nullable=False),
    Column('recurrence', RecurrenceTypeType, nullable=False, default=RecurrenceType.NONE),
    # TimedEvent specific columns (null for FullDayEntry)
    Column('start_time', Time, nullable=True),
    Column('end_time', Time, nullable=True),
)
