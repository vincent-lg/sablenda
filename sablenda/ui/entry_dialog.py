"""Dialog for viewing and editing day entries."""

from datetime import date, time

import wx

from sablenda.data.calendar import CalendarData
from sablenda.data.models import Entry, FullDayEntry, TimedEvent, RecurrenceType


class TimeInput(wx.TextCtrl):
    """A text input for time in HH:MM format with arrow key support."""

    def __init__(self, parent, initial_time: time = None):
        """Initialize the time input.

        Args:
            parent: Parent window
            initial_time: Initial time value

        """
        if initial_time is None:
            initial_time = time(9, 0)

        time_str = f"{initial_time.hour:02d}:{initial_time.minute:02d}"
        super().__init__(parent, value=time_str, size=(80, -1))

        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)

    def _on_key_down(self, event: wx.KeyEvent) -> None:
        """Handle up/down arrow keys to increment/decrement by 15 minutes."""
        key_code = event.GetKeyCode()

        if key_code in (wx.WXK_UP, wx.WXK_DOWN):
            try:
                current_time = self.get_time()
                if current_time:
                    # Calculate total minutes
                    total_minutes = current_time.hour * 60 + current_time.minute

                    # Increment or decrement by 15 minutes
                    if key_code == wx.WXK_UP:
                        total_minutes += 15
                    else:
                        total_minutes -= 15

                    # Wrap around at 24 hours
                    total_minutes = total_minutes % (24 * 60)
                    if total_minutes < 0:
                        total_minutes += 24 * 60

                    # Convert back to hours and minutes
                    hours = total_minutes // 60
                    minutes = total_minutes % 60

                    # Update the display
                    self.SetValue(f"{hours:02d}:{minutes:02d}")
                    return
            except ValueError:
                pass

        event.Skip()

    def get_time(self) -> time | None:
        """Parse and return the time value.

        Returns:
            time object or None if invalid

        """
        time_str = self.GetValue().strip()

        try:
            # Parse HH:MM format
            parts = time_str.split(':')
            if len(parts) == 2:
                hours = int(parts[0])
                minutes = int(parts[1])
                if 0 <= hours < 24 and 0 <= minutes < 60:
                    return time(hours, minutes)
        except (ValueError, IndexError):
            pass

        return None

    def set_time(self, t: time) -> None:
        """Set the time value.

        Args:
            t: Time to set

        """
        self.SetValue(f"{t.hour:02d}:{t.minute:02d}")


class EntryDialog(wx.Dialog):
    """Dialog for managing entries on a specific day."""

    def __init__(self, parent, day_date: date, calendar_data: CalendarData):
        """Initialize the entry dialog.

        Args:
            parent: Parent window
            day_date: The date being edited
            calendar_data: The calendar data model

        """
        super().__init__(
            parent,
            title=f"Entries for {day_date.strftime('%A, %B %d, %Y')}",
            size=(600, 500)
        )

        self.day_date = day_date
        self.calendar_data = calendar_data
        self.entries = calendar_data.get_entries_for_date(day_date)

        self._create_ui()
        self._update_entry_list()

    def _create_ui(self) -> None:
        """Create the dialog UI."""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # List of entries
        list_label = wx.StaticText(panel, label="Entries:")
        main_sizer.Add(list_label, 0, wx.ALL, 5)

        self.entry_listbox = wx.ListBox(panel, style=wx.LB_SINGLE)
        self.entry_listbox.Bind(wx.EVT_LISTBOX_DCLICK, self._on_edit_entry)
        main_sizer.Add(self.entry_listbox, 1, wx.ALL | wx.EXPAND, 5)

        # Buttons for entry management
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.add_fullday_btn = wx.Button(panel, label="Add Full-Day Entry")
        self.add_fullday_btn.Bind(wx.EVT_BUTTON, self._on_add_fullday)
        button_sizer.Add(self.add_fullday_btn, 0, wx.ALL, 5)

        self.add_timed_btn = wx.Button(panel, label="Add Timed Event")
        self.add_timed_btn.Bind(wx.EVT_BUTTON, self._on_add_timed)
        button_sizer.Add(self.add_timed_btn, 0, wx.ALL, 5)

        self.edit_btn = wx.Button(panel, label="Edit")
        self.edit_btn.Bind(wx.EVT_BUTTON, self._on_edit_entry)
        button_sizer.Add(self.edit_btn, 0, wx.ALL, 5)

        self.delete_btn = wx.Button(panel, label="Delete")
        self.delete_btn.Bind(wx.EVT_BUTTON, self._on_delete_entry)
        button_sizer.Add(self.delete_btn, 0, wx.ALL, 5)

        main_sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER, 5)

        # Close button
        close_btn = wx.Button(panel, wx.ID_CLOSE, "Close")
        close_btn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        main_sizer.Add(close_btn, 0, wx.ALL | wx.CENTER, 5)

        panel.SetSizer(main_sizer)

    def _update_entry_list(self) -> None:
        """Update the list of entries."""
        self.entry_listbox.Clear()
        self.entries = self.calendar_data.get_entries_for_date(self.day_date)

        for entry in self.entries:
            self.entry_listbox.Append(entry.get_display_text(), entry)

        # Enable/disable edit and delete buttons
        has_selection = self.entry_listbox.GetSelection() != wx.NOT_FOUND
        self.edit_btn.Enable(has_selection)
        self.delete_btn.Enable(has_selection)

    def _on_add_fullday(self, event: wx.Event) -> None:
        """Handle adding a full-day entry."""
        entry = FullDayEntry(entry_date=self.day_date)
        dlg = EntryEditDialog(self, entry, is_new=True)
        if dlg.ShowModal() == wx.ID_OK:
            self.calendar_data.add_entry(entry)
            self._update_entry_list()
        dlg.Destroy()

    def _on_add_timed(self, event: wx.Event) -> None:
        """Handle adding a timed event."""
        entry = TimedEvent(entry_date=self.day_date)
        dlg = EntryEditDialog(self, entry, is_new=True)
        if dlg.ShowModal() == wx.ID_OK:
            self.calendar_data.add_entry(entry)
            self._update_entry_list()
        dlg.Destroy()

    def _on_edit_entry(self, event: wx.Event) -> None:
        """Handle editing an entry."""
        selection = self.entry_listbox.GetSelection()
        if selection == wx.NOT_FOUND:
            return

        entry = self.entry_listbox.GetClientData(selection)
        if entry:
            dlg = EntryEditDialog(self, entry, is_new=False)
            if dlg.ShowModal() == wx.ID_OK:
                self.calendar_data.update_entry(entry)
                self._update_entry_list()
            dlg.Destroy()

    def _on_delete_entry(self, event: wx.Event) -> None:
        """Handle deleting an entry."""
        selection = self.entry_listbox.GetSelection()
        if selection == wx.NOT_FOUND:
            return

        entry = self.entry_listbox.GetClientData(selection)
        if entry:
            result = wx.MessageBox(
                f"Delete entry '{entry.get_display_text()}'?",
                "Confirm Delete",
                wx.YES_NO | wx.ICON_QUESTION
            )
            if result == wx.YES:
                self.calendar_data.remove_entry(entry.id)
                self._update_entry_list()


class EntryEditDialog(wx.Dialog):
    """Dialog for editing a single entry."""

    def __init__(self, parent, entry: Entry, is_new: bool):
        """Initialize the entry edit dialog.

        Args:
            parent: Parent window
            entry: The entry to edit
            is_new: Whether this is a new entry

        """
        title = "New Entry" if is_new else "Edit Entry"
        super().__init__(parent, title=title, size=(500, 400))

        self.entry = entry
        self.is_new = is_new

        self._create_ui()
        self._load_entry_data()

    def _create_ui(self) -> None:
        """Create the dialog UI."""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        title_label = wx.StaticText(panel, label="Title:")
        main_sizer.Add(title_label, 0, wx.ALL, 5)

        self.title_ctrl = wx.TextCtrl(panel)
        main_sizer.Add(self.title_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Description
        desc_label = wx.StaticText(panel, label="Description:")
        main_sizer.Add(desc_label, 0, wx.ALL, 5)

        self.desc_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        main_sizer.Add(self.desc_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        # Time fields for timed events
        if isinstance(self.entry, TimedEvent):
            time_sizer = wx.BoxSizer(wx.HORIZONTAL)

            start_label = wx.StaticText(panel, label="Start time (HH:MM):")
            time_sizer.Add(start_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

            self.start_time_ctrl = TimeInput(panel, self.entry.start_time)
            time_sizer.Add(self.start_time_ctrl, 0, wx.ALL, 5)

            end_label = wx.StaticText(panel, label="End time (HH:MM):")
            time_sizer.Add(end_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

            self.end_time_ctrl = TimeInput(panel, self.entry.end_time)
            time_sizer.Add(self.end_time_ctrl, 0, wx.ALL, 5)

            hint_text = wx.StaticText(panel, label="(Use ↑↓ arrows to adjust by 15 min)")
            hint_text.SetForegroundColour(wx.Colour(100, 100, 100))
            time_sizer.Add(hint_text, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

            main_sizer.Add(time_sizer, 0, wx.ALL, 5)

        # Recurrence
        recurrence_label = wx.StaticText(panel, label="Recurrence:")
        main_sizer.Add(recurrence_label, 0, wx.ALL, 5)

        recurrence_choices = [
            "None",
            "Daily",
            "Weekly",
            "Monthly",
            "Yearly"
        ]
        self.recurrence_ctrl = wx.Choice(panel, choices=recurrence_choices)
        self.recurrence_ctrl.SetSelection(0)
        main_sizer.Add(self.recurrence_ctrl, 0, wx.ALL, 5)

        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        ok_btn = wx.Button(panel, wx.ID_OK, "OK")
        ok_btn.Bind(wx.EVT_BUTTON, self._on_ok)
        button_sizer.Add(ok_btn, 0, wx.ALL, 5)

        cancel_btn = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        button_sizer.Add(cancel_btn, 0, wx.ALL, 5)

        main_sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER, 5)

        panel.SetSizer(main_sizer)

    def _load_entry_data(self) -> None:
        """Load entry data into the controls."""
        self.title_ctrl.SetValue(self.entry.title)
        self.desc_ctrl.SetValue(self.entry.description)

        # Set recurrence
        recurrence_map = {
            RecurrenceType.NONE: 0,
            RecurrenceType.DAILY: 1,
            RecurrenceType.WEEKLY: 2,
            RecurrenceType.MONTHLY: 3,
            RecurrenceType.YEARLY: 4
        }
        self.recurrence_ctrl.SetSelection(recurrence_map.get(self.entry.recurrence, 0))

    def _on_ok(self, event: wx.Event) -> None:
        """Handle OK button - save changes to entry."""
        self.entry.title = self.title_ctrl.GetValue()
        self.entry.description = self.desc_ctrl.GetValue()

        if isinstance(self.entry, TimedEvent):
            start_time = self.start_time_ctrl.get_time()
            end_time = self.end_time_ctrl.get_time()

            if start_time is None or end_time is None:
                wx.MessageBox(
                    "Please enter valid times in HH:MM format (e.g., 09:00)",
                    "Invalid Time",
                    wx.OK | wx.ICON_ERROR
                )
                return

            self.entry.start_time = start_time
            self.entry.end_time = end_time

        # Set recurrence
        recurrence_map = [
            RecurrenceType.NONE,
            RecurrenceType.DAILY,
            RecurrenceType.WEEKLY,
            RecurrenceType.MONTHLY,
            RecurrenceType.YEARLY
        ]
        self.entry.recurrence = recurrence_map[self.recurrence_ctrl.GetSelection()]

        self.EndModal(wx.ID_OK)
