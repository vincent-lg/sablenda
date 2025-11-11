"""Main application window."""

import wx
import wx.adv

from sablenda.data.calendar import CalendarData
from sablenda.i18n import get_i18n, init_i18n
from sablenda.infrastructure.database import DatabaseConfig
from sablenda.infrastructure.sqlalchemy_repository import SqlAlchemyCalendarRepository
from sablenda.settings import Settings, save_settings
from sablenda.ui.calendar_grid import CalendarGrid
from sablenda.ui.preferences_dialog import PreferencesDialog


class MainWindow(wx.Frame):
    """Main application window."""

    def __init__(self, settings: Settings):
        """Initialize the main window."""
        self.settings = settings
        self.i18n = get_i18n()

        super().__init__(
            None,
            title=self.i18n.translate("app-title"),
            size=(800, 700)
        )

        # Initialize database and repository
        self.db_config = DatabaseConfig()
        self.repository = SqlAlchemyCalendarRepository(self.db_config)

        # Initialize calendar data with repository
        self.calendar_data = CalendarData(repository=self.repository)

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
        save_item = file_menu.Append(
            wx.ID_SAVE,
            f"{self.i18n.translate('menu-save')}\t{self.i18n.translate('menu-save-accelerator')}",
            self.i18n.translate('menu-save-help')
        )
        self.Bind(wx.EVT_MENU, self._on_save, save_item)

        preferences_item = file_menu.Append(
            wx.ID_PREFERENCES,
            self.i18n.translate('menu-preferences'),
            self.i18n.translate('menu-preferences-help')
        )
        self.Bind(wx.EVT_MENU, self._on_preferences, preferences_item)

        file_menu.AppendSeparator()
        exit_item = file_menu.Append(
            wx.ID_EXIT,
            f"{self.i18n.translate('menu-exit')}\t{self.i18n.translate('menu-exit-accelerator')}",
            self.i18n.translate('menu-exit-help')
        )
        self.Bind(wx.EVT_MENU, self._on_close, exit_item)

        # Help menu
        help_menu = wx.Menu()
        about_item = help_menu.Append(
            wx.ID_ABOUT,
            self.i18n.translate('menu-about'),
            self.i18n.translate('menu-about-help')
        )
        self.Bind(wx.EVT_MENU, self._on_about, about_item)

        menubar.Append(file_menu, self.i18n.translate('menu-file'))
        menubar.Append(help_menu, self.i18n.translate('menu-help'))

        self.SetMenuBar(menubar)

    def _on_save(self, event: wx.Event) -> None:
        """Handle save action."""
        # With SQLAlchemy repository, data is automatically persisted
        # This method is kept for UI consistency but just confirms the save
        try:
            self.repository.save_changes()
            wx.MessageBox(
                self.i18n.translate("save-success"),
                self.i18n.translate("save-title"),
                wx.OK | wx.ICON_INFORMATION
            )
        except Exception as e:
            wx.MessageBox(
                self.i18n.translate("save-error", error=str(e)),
                self.i18n.translate("save-error-title"),
                wx.OK | wx.ICON_ERROR
            )

    def _on_close(self, event: wx.Event) -> None:
        """Handle window close - ensure data is saved and exit."""
        try:
            # Ensure any pending changes are saved
            self.repository.save_changes()
            # Close the repository session
            self.repository.close()
        except Exception as e:
            result = wx.MessageBox(
                self.i18n.translate("save-error-exit", error=str(e)),
                self.i18n.translate("save-error-title"),
                wx.YES_NO | wx.ICON_ERROR
            )
            if result != wx.YES:
                event.Veto()
                return

        self.Destroy()

    def _on_preferences(self, event: wx.Event) -> None:
        """Show preferences dialog."""
        dialog = PreferencesDialog(self, self.settings)
        if dialog.ShowModal() == wx.ID_OK:
            # Save settings
            save_settings(self.settings)

            # Reinitialize i18n with new language
            init_i18n(self.settings)
            self.i18n = get_i18n()

            # Refresh UI
            self._refresh_ui()

        dialog.Destroy()

    def _refresh_ui(self) -> None:
        """Refresh UI after language change."""
        # Update window title
        self.SetTitle(self.i18n.translate("app-title"))

        # Recreate menu bar
        self.SetMenuBar(None)
        self._create_menu()

        # Refresh calendar grid
        self.calendar_grid.refresh_ui()

    def _on_about(self, event: wx.Event) -> None:
        """Show about dialog."""
        info = wx.adv.AboutDialogInfo()
        info.SetName(self.i18n.translate("about-name"))
        info.SetVersion(self.i18n.translate("about-version"))
        info.SetDescription(self.i18n.translate("about-description"))
        info.AddDeveloper(self.i18n.translate("about-developer"))
        wx.adv.AboutBox(info)
