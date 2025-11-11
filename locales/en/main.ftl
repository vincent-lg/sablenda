# Main window
app-title = Le Sablenda

# Menu items
menu-file = &File
menu-help = &Help
menu-save = &Save
menu-save-accelerator = Ctrl+S
menu-save-help = Save the agenda
menu-preferences = &Preferences...
menu-preferences-help = Configure application settings
menu-exit = E&xit
menu-exit-accelerator = Ctrl+Q
menu-exit-help = Exit the application
menu-about = &About
menu-about-help = About the agenda

# Save messages
save-success = Agenda saved successfully!
save-title = Save
save-error = Error saving agenda: {$error}
save-error-title = Save Error
save-error-exit = Error saving agenda: {$error}

    Exit anyway?

# About dialog
about-name = Le Sablenda
about-version = 1.0
about-description = An accessible calendar application built with wxPython
about-developer = Created with Claude Code

# Calendar grid - abbreviated day names
day-mon = Mon
day-tue = Tue
day-wed = Wed
day-thu = Thu
day-fri = Fri
day-sat = Sat
day-sun = Sun

# Date formatting
# Format: "Monday, November 4th, 2025"
date-full = { $weekday }, { $month } { $day }{ $ordinal }, { $year }
# Format: "November 2025"
date-month-year = { $month } { $year }
# Format: "Monday, November 04, 2025" (for dialog titles)
date-dialog-title = { $weekday }, { $month } { $day }, { $year }

# Ordinal suffixes for dates
ordinal-1 = st
ordinal-2 = nd
ordinal-3 = rd
ordinal-other = th

# Full day names
day-name-0 = Monday
day-name-1 = Tuesday
day-name-2 = Wednesday
day-name-3 = Thursday
day-name-4 = Friday
day-name-5 = Saturday
day-name-6 = Sunday

# Month names
month-name-1 = January
month-name-2 = February
month-name-3 = March
month-name-4 = April
month-name-5 = May
month-name-6 = June
month-name-7 = July
month-name-8 = August
month-name-9 = September
month-name-10 = October
month-name-11 = November
month-name-12 = December

# Entry count
entry-count = {$count ->
    [one] {$count} entry
    *[other] {$count} entries
}

# Entry dialog
entries-for-date = Entries for {$date}
entries-label = Entries:
title-label = Title:
description-label = Description:
start-time-label = Start time (HH:MM):
end-time-label = End time (HH:MM):
time-hint = (Use ↑↓ arrows to adjust by 15 min)
recurrence-label = Recurrence:

# Buttons
btn-add-fullday = Add Full-Day Entry
btn-add-timed = Add Timed Event
btn-edit = Edit
btn-delete = Delete
btn-close = Close
btn-ok = OK
btn-cancel = Cancel

# Dialog titles
dialog-new-entry = New Entry
dialog-edit-entry = Edit Entry

# Recurrence types
recurrence-none = None
recurrence-daily = Daily
recurrence-weekly = Weekly
recurrence-monthly = Monthly
recurrence-yearly = Yearly

# Messages
confirm-delete = Delete entry '{$title}'?
confirm-delete-title = Confirm Delete
invalid-time = Please enter valid times in HH:MM format (e.g., 09:00)
invalid-time-title = Invalid Time

# Default values
default-title = Untitled

# Preferences dialog
preferences-title = Preferences
preferences-language-label = Language:
preferences-language-auto = Automatic (system default)
preferences-language-en = English
preferences-language-fr = French
