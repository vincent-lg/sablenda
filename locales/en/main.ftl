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
save-error = Error saving agenda: { $error }
save-error-title = Save Error
save-error-exit = Error saving agenda: { $error }

    Exit anyway?

# About dialog
about-name = Le Sablenda
about-version = 1.0
about-description = An accessible calendar application built with wxPython
about-developer = Vincent Le Goff, created with Claude Code

# Calendar grid - abbreviated day names
day-mon = Mon
day-tue = Tue
day-wed = Wed
day-thu = Thu
day-fri = Fri
day-sat = Sat
day-sun = Sun

# Entry count
entry-count = {$count ->
    [one] {$count} entry
    *[other] { $count } entries
}

# Entry dialog
entries-for-date = Entries for { $date }
entries-label = Entries:
title-label = Title:
description-label = Description:
start-time-label = Start time (HH:MM):
end-time-label = End time (HH:MM):
time-hint = (Use up/down arrow keys to adjust by 15 min)
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
confirm-delete = Delete entry '{ $title }'?
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
