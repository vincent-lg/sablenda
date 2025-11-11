"""Main entry point for the agenda application."""

import wx

from sablenda.i18n import init_i18n
from sablenda.settings import load_settings
from sablenda.ui.main_window import MainWindow


def main():
    """Run the application."""
    # Load settings
    settings = load_settings()

    # Initialize i18n
    i18n = init_i18n(settings)

    # Create and run application
    app = wx.App()
    frame = MainWindow(settings)
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
