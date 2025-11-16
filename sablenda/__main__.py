"""Main entry point for the agenda application."""

import argparse
import logging
import wx

from sablenda.i18n import init_i18n
from sablenda.ipc import NamedPipeClient
from sablenda.settings import load_settings
from sablenda.ui.main_window import MainWindow
from sablenda.ui.tray_icon import TrayIcon

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


def main():
    """Run the application."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Le Sablenda - Accessible calendar application"
    )
    parser.add_argument(
        "--tray",
        action="store_true",
        help="Start in system tray mode (runs in background)"
    )
    args = parser.parse_args()

    if args.tray:
        # Tray mode: run as background service
        _run_tray_mode()
    else:
        # Default mode: show window or connect to existing instance
        _run_normal_mode()


def _run_tray_mode():
    """Run the application in system tray mode."""
    log.debug("Starting Sablenda in tray mode")

    # Load settings
    settings = load_settings()

    # Initialize i18n
    init_i18n(settings)

    # Create and run application
    app = wx.App()
    frame = MainWindow(settings, tray_mode=True)

    # Create tray icon
    tray = TrayIcon(frame, frame.calendar_data)

    # Start hidden and iconized to tray (don't Show() - that makes it visible)
    frame.Hide()
    frame.Iconize(True)

    log.debug("Entering tray mode main loop")
    app.MainLoop()

    log.debug("Sablenda tray mode stopped")


def _run_normal_mode():
    """Run the application in normal mode (show window or connect to instance)."""
    log.debug("Starting Sablenda in normal mode")

    # Try to connect to existing tray instance with retries
    # Wait a moment to ensure server is ready if it was just started
    for attempt in range(3):
        if NamedPipeClient.send_command("focus"):
            log.debug(f"Connected to existing instance on attempt {attempt + 1}")
            return
        if attempt < 2:
            import time
            time.sleep(0.5)

    # No existing instance, start normally
    log.debug("No existing instance found, starting normal window")

    # Load settings
    settings = load_settings()

    # Initialize i18n
    init_i18n(settings)

    # Create and run application
    app = wx.App()
    frame = MainWindow(settings)
    frame.Show()
    app.MainLoop()

    log.debug("Sablenda normal mode stopped")


if __name__ == "__main__":
    main()
