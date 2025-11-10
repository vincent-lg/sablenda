# Accessible Agenda

An accessible calendar application written in Python using wxPython, designed with screen reader support.

## Features

- Monthly calendar view with day buttons
- Accessible labels for screen readers (full date + entry count)
- Two types of entries:
  - Full-day entries (birthdays, reminders, etc.)
  - Timed events (with start and end times)
- Recurring entries (daily, weekly, monthly, yearly)
- Visual indicators for days with entries (color highlighting)
- Keyboard navigation:
  - Arrow keys: navigate between days
  - Up/Down arrows: navigate by week
  - Ctrl+Up/Down: change months
- Automatic data persistence using pickle

## Installation

This project uses `uv` for dependency management. To set up:

```bash
uv sync
```

## Running

```bash
uv run python main.py
```

## Usage

### Navigation
- Use arrow keys to move between days
- Use Up/Down arrows to move by week
- Use Ctrl+Up/Down to change months
- Press Enter or Space on a day to view/edit entries

### Managing Entries
- Click or press Enter on any day to open the entry dialog
- Add full-day entries (e.g., birthdays, holidays)
- Add timed events with specific start/end times
- Set recurrence patterns for repeating events
- Edit or delete existing entries

### Accessibility
- Each day button announces the full date to screen readers
- Days with entries announce the entry count
- All dialogs and controls are keyboard accessible

## Project Structure

```
agenda/
├── data/           # Data models and calendar logic
│   ├── models.py   # Entry classes (FullDayEntry, TimedEvent)
│   └── calendar.py # Calendar data management
├── storage/        # Persistence layer
│   └── pickle_storage.py
└── ui/             # User interface components
    ├── calendar_grid.py  # Main calendar grid
    ├── entry_dialog.py   # Entry management dialogs
    └── main_window.py    # Main application window
```

## Data Storage

The agenda automatically saves to `agenda_data.pkl` in the current directory. Data is saved when:
- The application closes
- You manually save via File > Save (Ctrl+S)
