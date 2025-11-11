"""Main entry point for the agenda application."""

import wx

from sablenda.ui.main_window import MainWindow


def main():
    """Run the application."""
    app = wx.App()
    frame = MainWindow()
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
