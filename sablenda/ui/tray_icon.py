"""System tray icon and menu for Sablenda."""

import logging
import wx
import wx.adv

from datetime import date
from sablenda.data.calendar import CalendarData
from sablenda.i18n import get_i18n
from sablenda.ipc import NamedPipeServer
from sablenda.windows_api import focus_window_robust

log = logging.getLogger(__name__)


class TrayIcon(wx.adv.TaskBarIcon):
    """System tray icon with context menu."""

    def __init__(self, main_window: wx.Frame, calendar_data: CalendarData):
        """
        Initialize the tray icon.

        Args:
            main_window: The main application window
            calendar_data: The calendar data for retrieving today's entries
        """
        super().__init__()
        self.main_window = main_window
        self.calendar_data = calendar_data
        self.i18n = get_i18n()
        self.pipe_server: NamedPipeServer | None = None

        # Set the icon
        self._set_icon()

        # Bind events
        self.Bind(wx.adv.EVT_TASKBAR_RIGHT_DOWN, self._on_right_click)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self._on_left_click)

        # Start the pipe server for receiving commands from other instances
        self._start_pipe_server()

        log.debug("Tray icon initialized")

    def _set_icon(self) -> None:
        """Set the tray icon from application resources."""
        # For now, use a simple colored icon
        # In a real app, this would load a proper icon from resources
        icon = wx.Icon()
        # Create a simple 16x16 icon
        bmp = wx.Bitmap(16, 16)
        dc = wx.MemoryDC(bmp)
        dc.SetBrush(wx.Brush(wx.Colour(70, 130, 180)))  # Steel blue
        dc.DrawRectangle(0, 0, 16, 16)
        dc.SelectObject(wx.NullBitmap)
        icon.CopyFromBitmap(bmp)

        self.SetIcon(icon, self.i18n.translate("app-title"))

    def _on_left_click(self, event: wx.Event) -> None:
        """Handle left-click on tray icon - show/focus the window."""
        self._show_window()

    def _on_right_click(self, event: wx.Event) -> None:
        """Handle right-click on tray icon - show context menu."""
        self._show_menu()

    def _show_menu(self) -> None:
        """Display the context menu."""
        menu = wx.Menu()

        # Show/Open option
        show_item = menu.Append(
            wx.ID_ANY,
            self.i18n.translate("tray-show"),
            self.i18n.translate("tray-show-help")
        )
        self.Bind(wx.EVT_MENU, lambda e: self._show_window(), show_item)

        menu.AppendSeparator()

        # Today's entries
        today_entries = self.calendar_data.get_entries_for_date(date.today())
        if today_entries:
            entries_item = menu.Append(
                wx.ID_ANY,
                self.i18n.translate("tray-today-entries"),
                self.i18n.translate("tray-today-entries-help"),
                wx.ITEM_NORMAL
            )
            entries_item.Enable(False)

            for entry in today_entries:
                entry_item = menu.Append(
                    wx.ID_ANY,
                    str(entry),
                    "",
                    wx.ITEM_NORMAL
                )
                entry_item.Enable(False)

            menu.AppendSeparator()
        else:
            no_entries_item = menu.Append(
                wx.ID_ANY,
                self.i18n.translate("tray-no-entries"),
                "",
                wx.ITEM_NORMAL
            )
            no_entries_item.Enable(False)
            menu.AppendSeparator()

        # Exit option
        exit_item = menu.Append(
            wx.ID_EXIT,
            self.i18n.translate("menu-exit"),
            self.i18n.translate("menu-exit-help")
        )
        self.Bind(wx.EVT_MENU, lambda e: self._exit_application(), exit_item)

        self.PopupMenu(menu)

    def _show_window(self) -> None:
        """Show and focus the main window using robust Windows API methods."""
        log.debug(f"_show_window called - IsIconized: {self.main_window.IsIconized()}, IsShown: {self.main_window.IsShown()}")

        try:
            # First, restore from minimized state if needed
            if self.main_window.IsIconized():
                log.debug("Window is iconized, restoring...")
                self.main_window.Iconize(False)

            # Show the window if it's hidden
            if not self.main_window.IsShown():
                log.debug("Window is hidden, showing...")
                self.main_window.Show(True)

            # Use robust Windows API to focus the window
            # This handles focus-stealing prevention and ensures screen readers perceive the window
            hwnd = self.main_window.GetHandle()
            if hwnd:
                log.debug("Using Windows API for robust window focus...")
                focus_window_robust(hwnd)
            else:
                log.warning("Could not get window handle, using wxPython methods instead")
                self.main_window.Raise()
                self.main_window.SetFocus()

            log.debug(f"Window state after show - IsIconized: {self.main_window.IsIconized()}, IsShown: {self.main_window.IsShown()}")
        except Exception as e:
            log.error(f"Error showing window: {e}", exc_info=True)

    def _exit_application(self) -> None:
        """Exit the application."""
        self.RemoveIcon()
        self._stop_pipe_server()
        wx.GetApp().ExitMainLoop()

    def _start_pipe_server(self) -> None:
        """Start the named pipe server for receiving commands."""
        try:
            self.pipe_server = NamedPipeServer(self._on_pipe_command)
            self.pipe_server.start()
        except Exception as e:
            log.error(f"Failed to start pipe server: {e}")

    def _stop_pipe_server(self) -> None:
        """Stop the named pipe server."""
        if self.pipe_server:
            try:
                self.pipe_server.stop()
            except Exception as e:
                log.error(f"Error stopping pipe server: {e}")
            self.pipe_server = None

    def _on_pipe_command(self, command: dict) -> None:
        """Handle a command received from the named pipe."""
        action = command.get("action")
        log.debug(f"Received pipe command: {action}")

        if action == "focus":
            # Show and focus the window
            wx.CallAfter(self._show_window)
        elif action == "toggle":
            # Toggle visibility
            if self.main_window.IsIconized() or not self.main_window.IsShown():
                wx.CallAfter(self._show_window)
            else:
                wx.CallAfter(self.main_window.Iconize, True)
        else:
            log.warning(f"Unknown pipe command: {action}")

    def Destroy(self) -> None:
        """Clean up when the tray icon is destroyed."""
        self._stop_pipe_server()
        super().Destroy()
