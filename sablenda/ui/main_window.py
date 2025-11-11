"""Main application window."""

import wx

from sablenda.data.calendar import CalendarData
from sablenda.storage.pickle_storage import PickleStorage
from sablenda.ui.calendar_grid import CalendarGrid


class MainWindow(wx.Frame):
    """Main application window."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__(
            None,
            title="Le Sablenda",
            size=(800, 700)
        )

        # Initialize storage and load data
        self.storage = PickleStorage()
        self.calendar_data = self.storage.load()

        # Create UI
        self._create_ui()
        self._create_menu()

        # Bind close event to save data
        self.Bind(wx.EVT_CLOSE, self._on_close)

        self.Centre()

    def _create_ui(self) -> None:
        """Create the UI."""
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Calendar grid
        self.calendar_grid = CalendarGrid(panel, self.calendar_data)
        sizer.Add(self.calendar_grid, 1, wx.ALL | wx.EXPAND, 10)

        panel.SetSizer(sizer)

    def _create_menu(self) -> None:
        """Create the menu bar."""
        menubar = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()
        save_item = file_menu.Append(wx.ID_SAVE, "&Save\tCtrl+S", "Save the agenda")
        self.Bind(wx.EVT_MENU, self._on_save, save_item)
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, "E&xit\tCtrl+Q", "Exit the application")
        self.Bind(wx.EVT_MENU, self._on_close, exit_item)

        # Help menu
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "&About", "About the agenda")
        self.Bind(wx.EVT_MENU, self._on_about, about_item)

        menubar.Append(file_menu, "&File")
        menubar.Append(help_menu, "&Help")

        self.SetMenuBar(menubar)

    def _on_save(self, event: wx.Event) -> None:
        """Handle save action."""
        try:
            self.storage.save(self.calendar_data)
            wx.MessageBox(
                "Agenda saved successfully!",
                "Save",
                wx.OK | wx.ICON_INFORMATION
            )
        except Exception as e:
            wx.MessageBox(
                f"Error saving agenda: {e}",
                "Save Error",
                wx.OK | wx.ICON_ERROR
            )

    def _on_close(self, event: wx.Event) -> None:
        """Handle window close - save data and exit."""
        try:
            self.storage.save(self.calendar_data)
        except Exception as e:
            result = wx.MessageBox(
                f"Error saving agenda: {e}\n\nExit anyway?",
                "Save Error",
                wx.YES_NO | wx.ICON_ERROR
            )
            if result != wx.YES:
                event.Veto()
                return

        self.Destroy()

    def _on_about(self, event: wx.Event) -> None:
        """Show about dialog."""
        info = wx.adv.AboutDialogInfo()
        info.SetName("Accessible Agenda")
        info.SetVersion("1.0")
        info.SetDescription("An accessible calendar application built with wxPython")
        info.AddDeveloper("Created with Claude Code")
        wx.adv.AboutBox(info)
