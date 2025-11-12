"""Calendar grid UI component."""

import calendar
from datetime import date, timedelta

import wx

from sablenda.data.calendar import CalendarData
from sablenda.i18n import get_i18n
from sablenda.ui.entry_dialog import EntryDialog


class DayButtonAccessible(wx.Accessible):
    """Custom accessible object for day buttons."""

    def __init__(self, button):
        """Initialize the accessible object.

        Args:
            button: The DayButton this accessible object is for

        """
        super().__init__(button)
        self.button = button

    def GetName(self, child_id):
        """Return the accessible name for screen readers.

        Args:
            child_id: The child ID (0 for the object itself)

        Returns:
            Tuple of (result_code, name_string)

        """
        if child_id == wx.ACC_SELF:
            i18n = get_i18n()

            # Format date using i18n
            accessible_text = i18n.format_date_full(self.button.day_date, capitalize=True)

            # Add entry count if present
            if self.button.entry_count > 0:
                entry_count_text = i18n.translate("entry-count", count=self.button.entry_count)
                accessible_text += f", {entry_count_text}"

            return wx.ACC_OK, accessible_text

        return wx.ACC_NOT_IMPLEMENTED, None

    def GetRole(self, child_id):
        """Return the role of this object.

        Args:
            child_id: The child ID (0 for the object itself)

        Returns:
            Tuple of (result_code, role)

        """
        if child_id == wx.ACC_SELF:
            return wx.ACC_OK, wx.ROLE_SYSTEM_PUSHBUTTON
        return wx.ACC_NOT_IMPLEMENTED, None


class DayButton(wx.Button):
    """A button representing a single day in the calendar."""

    def __init__(self, parent, day_date: date, is_current_month: bool):
        """Initialize a day button.

        Args:
            parent: Parent window
            day_date: The date this button represents
            is_current_month: Whether this day is in the currently displayed month

        """
        super().__init__(parent, label=str(day_date.day))
        self.day_date = day_date
        self.is_current_month = is_current_month
        self.entry_count = 0

        # Set initial colors based on whether it's in current month
        if not is_current_month:
            self.SetForegroundColour(wx.Colour(150, 150, 150))

        # Set the custom accessible object for screen readers
        self.SetAccessible(DayButtonAccessible(self))

        self._update_accessible_label()

    def set_entry_count(self, count: int) -> None:
        """Set the number of entries for this day and update display."""
        self.entry_count = count
        self._update_accessible_label()

        # Highlight days with entries
        if count > 0 and self.is_current_month:
            self.SetBackgroundColour(wx.Colour(220, 240, 255))
        else:
            self.SetBackgroundColour(wx.NullColour)

        self.Refresh()

    def _update_accessible_label(self) -> None:
        """Update the visual label and tooltip."""
        i18n = get_i18n()

        # Keep the visual label as just the day number
        self.SetLabel(str(self.day_date.day))

        # Set tooltip (the accessible name is handled by DayButtonAccessible)
        tooltip_text = i18n.format_date_full(self.day_date, capitalize=True)

        # Add entry count if present
        if self.entry_count > 0:
            entry_count_text = i18n.translate("entry-count", count=self.entry_count)
            tooltip_text += f" ({entry_count_text})"

        # Set as tooltip for mouse hover
        self.SetToolTip(tooltip_text)


class CalendarGrid(wx.Panel):
    """Main calendar grid displaying a month view."""

    def __init__(self, parent, calendar_data: CalendarData):
        """Initialize the calendar grid.

        Args:
            parent: Parent window
            calendar_data: The calendar data model

        """
        super().__init__(parent)
        self.calendar_data = calendar_data
        self.current_date = date.today()
        self.day_buttons: list[DayButton] = []
        self._initial_display = True

        self._create_ui()
        self._update_calendar_display()

    def _create_ui(self) -> None:
        """Create the UI layout."""
        i18n = get_i18n()
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Month/Year label
        self.month_label = wx.StaticText(self, label="")
        font = self.month_label.GetFont()
        font.PointSize += 4
        font = font.Bold()
        self.month_label.SetFont(font)
        main_sizer.Add(self.month_label, 0, wx.ALL | wx.CENTER, 10)

        # Grid for days
        self.grid_sizer = wx.GridSizer(rows=7, cols=7, vgap=2, hgap=2)

        # Add day headers (Mon, Tue, Wed, etc.)
        self.day_headers = []
        for day_key in ['day-mon', 'day-tue', 'day-wed', 'day-thu', 'day-fri', 'day-sat', 'day-sun']:
            header = wx.StaticText(self, label=i18n.translate(day_key))
            header_font = header.GetFont()
            header_font = header_font.Bold()
            header.SetFont(header_font)
            self.grid_sizer.Add(header, 0, wx.ALIGN_CENTER)
            self.day_headers.append(header)

        # Create day buttons (will be populated later)
        # Create enough for 6 weeks (42 days)
        for i in range(42):
            btn = DayButton(self, date.today(), True)
            btn.Bind(wx.EVT_BUTTON, self._on_day_clicked)
            self.grid_sizer.Add(btn, 1, wx.EXPAND)
            self.day_buttons.append(btn)

        main_sizer.Add(self.grid_sizer, 1, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(main_sizer)

        # Bind keyboard navigation at the panel level using CHAR_HOOK
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

    def _update_calendar_display(self) -> None:
        """Update the calendar to show the current month."""
        self.Freeze()

        # Update month label
        i18n = get_i18n()
        month_label_text = i18n.format_month_year(self.current_date.month, self.current_date.year)
        self.month_label.SetLabel(month_label_text)

        # Get all days to display
        days = self.calendar_data.get_month_days(
            self.current_date.year,
            self.current_date.month
        )

        # Update each button
        for i, day_date in enumerate(days):
            if i < len(self.day_buttons):
                btn = self.day_buttons[i]
                is_current_month = day_date.month == self.current_date.month

                # Update button data
                btn.day_date = day_date
                btn.is_current_month = is_current_month

                # Update colors for non-current month days
                if not is_current_month:
                    btn.SetForegroundColour(wx.Colour(150, 150, 150))
                else:
                    btn.SetForegroundColour(wx.NullColour)

                # Update entry count and accessible labels (this also sets the visual label)
                entry_count = self.calendar_data.get_entry_count_for_date(day_date)
                btn.set_entry_count(entry_count)

                btn.Show()

        # Hide any extra buttons
        for i in range(len(days), len(self.day_buttons)):
            self.day_buttons[i].Hide()

        self.Layout()

        # Focus on today's date when initially opening the agenda
        if self._initial_display:
            self._initial_display = False
            today = date.today()
            for btn in self.day_buttons:
                if btn.IsShown() and btn.day_date == today:
                    btn.SetFocus()
                    break

        self.Thaw()
    def _on_day_clicked(self, event: wx.Event) -> None:
        """Handle day button click."""
        btn = event.GetEventObject()
        if isinstance(btn, DayButton):
            dlg = EntryDialog(self, btn.day_date, self.calendar_data)
            dlg.ShowModal()
            dlg.Destroy()
            # Refresh display in case entries were added/modified
            self.refresh_display()

    def _on_char_hook(self, event: wx.KeyEvent) -> None:
        """Handle keyboard navigation using CHAR_HOOK."""
        key_code = event.GetKeyCode()
        ctrl_down = event.ControlDown()

        # Get the currently focused button
        focused_btn = wx.Window.FindFocus()
        if not isinstance(focused_btn, DayButton):
            event.Skip()
            return

        current_date = focused_btn.day_date
        new_date = None

        # Month navigation with Ctrl+Up/Down
        if ctrl_down and key_code == wx.WXK_UP:
            self._navigate_month(-1, current_date)
            return
        elif ctrl_down and key_code == wx.WXK_DOWN:
            self._navigate_month(1, current_date)
            return

        # Year navigation with Page Up/Down
        if key_code == wx.WXK_PAGEUP:
            self._navigate_year(-1, current_date)
            return
        elif key_code == wx.WXK_PAGEDOWN:
            self._navigate_year(1, current_date)
            return

        # Day navigation
        if key_code == wx.WXK_LEFT:
            # Previous day
            new_date = current_date - timedelta(days=1)
        elif key_code == wx.WXK_RIGHT:
            # Next day
            new_date = current_date + timedelta(days=1)
        elif key_code == wx.WXK_UP:
            # Previous week
            new_date = current_date - timedelta(days=7)
        elif key_code == wx.WXK_DOWN:
            # Next week
            new_date = current_date + timedelta(days=7)
        else:
            event.Skip()
            return

        # Navigate to the new date
        if new_date:
            self._navigate_to_date(new_date)

    def _navigate_to_date(self, target_date: date) -> None:
        """Navigate to a specific date, changing month if necessary."""
        # Check if we need to change the displayed month
        if target_date.month != self.current_date.month or target_date.year != self.current_date.year:
            self.current_date = date(target_date.year, target_date.month, 1)
            self._update_calendar_display()

        # Find and focus the button for the target date
        for btn in self.day_buttons:
            if btn.IsShown() and btn.day_date == target_date:
                btn.SetFocus()
                break

    def _navigate_month(self, offset: int, current_date: date) -> None:
        """Navigate to the next or previous month, keeping the same day if possible."""
        month = current_date.month + offset
        year = current_date.year
        day = current_date.day

        while month > 12:
            month -= 12
            year += 1
        while month < 1:
            month += 12
            year -= 1

        # Handle day overflow (e.g., Jan 31 -> Feb 28)
        import calendar as cal
        max_day = cal.monthrange(year, month)[1]
        day = min(day, max_day)

        target_date = date(year, month, day)
        self._navigate_to_date(target_date)

    def _navigate_year(self, offset: int, current_date: date) -> None:
        """Navigate to the next or previous year, keeping the same month and day if possible."""
        year = current_date.year + offset
        month = current_date.month
        day = current_date.day

        # Handle leap year case (Feb 29 -> Feb 28)
        import calendar as cal
        max_day = cal.monthrange(year, month)[1]
        day = min(day, max_day)

        target_date = date(year, month, day)
        self._navigate_to_date(target_date)

    def change_month(self, offset: int) -> None:
        """Change the displayed month by the given offset."""
        month = self.current_date.month + offset
        year = self.current_date.year

        while month > 12:
            month -= 12
            year += 1
        while month < 1:
            month += 12
            year -= 1

        # Update to first day of new month
        self.current_date = date(year, month, 1)
        self._update_calendar_display()

    def refresh_display(self) -> None:
        """Refresh the calendar display (e.g., after adding/editing entries)."""
        self._update_calendar_display()

    def refresh_ui(self) -> None:
        """Refresh UI elements after language change."""
        i18n = get_i18n()

        # Update day headers
        day_keys = ['day-mon', 'day-tue', 'day-wed', 'day-thu', 'day-fri', 'day-sat', 'day-sun']
        for i, header in enumerate(self.day_headers):
            header.SetLabel(i18n.translate(day_keys[i]))

        # Update month label
        month_label_text = i18n.format_month_year(self.current_date.month, self.current_date.year)
        self.month_label.SetLabel(month_label_text)

        # Update all day button tooltips and accessible labels
        for btn in self.day_buttons:
            if btn.IsShown():
                btn._update_accessible_label()

        self.Layout()
