"""Classical mapping configuration between domain models and database schema.

This module sets up the mapping between domain models (Entry, FullDayEntry, TimedEvent)
and the database tables using SQLAlchemy's classical mapping approach.

"""

from sqlalchemy.orm import registry

from sablenda.data.models import Entry, FullDayEntry, TimedEvent, RecurrenceType
from sablenda.infrastructure.schema import entries_table

# Create mapper registry
mapper_registry = registry()


def configure_mappings() -> None:
    """Configure classical mappings between domain models and database schema.

    Uses single table inheritance to store all entry types in one table,
    with a discriminator column to distinguish between entry types.

    """
    # Map the base Entry class
    mapper_registry.map_imperatively(
        Entry,
        entries_table,
        polymorphic_on=entries_table.c.entry_type,
        polymorphic_identity='entry',
        properties={
            'id': entries_table.c.id,
            'title': entries_table.c.title,
            'description': entries_table.c.description,
            'entry_date': entries_table.c.entry_date,
            'recurrence': entries_table.c.recurrence,
        }
    )

    # Map FullDayEntry subclass
    mapper_registry.map_imperatively(
        FullDayEntry,
        inherits=Entry,
        polymorphic_identity='full_day',
    )

    # Map TimedEvent subclass
    mapper_registry.map_imperatively(
        TimedEvent,
        inherits=Entry,
        polymorphic_identity='timed',
        properties={
            'start_time': entries_table.c.start_time,
            'end_time': entries_table.c.end_time,
        }
    )


# Initialize mappings when module is imported
configure_mappings()
