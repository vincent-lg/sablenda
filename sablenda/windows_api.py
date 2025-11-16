"""Windows API utilities for window management and focus."""

import ctypes
import ctypes.wintypes
import logging
import time

log = logging.getLogger(__name__)


class WindowsAPI:
    """Organized Windows API functions for window management.

    This class encapsulates all Windows API function declarations used for
    window management and focus operations to provide a cleaner namespace
    and better organization.
    """

    def __init__(self):
        """Initialize Windows API function bindings."""
        self.kernel32 = ctypes.windll.kernel32
        self.user32 = ctypes.windll.user32
        self._setup_window_management()

    def _setup_window_management(self):
        """Set up window management API functions.

        Configures Windows User32 API functions for window focusing, positioning,
        and thread management. These functions are essential for robust window
        focusing that can bypass Windows focus stealing prevention.
        """
        # SetForegroundWindow - Brings a window to the foreground and activates it
        self.SetForegroundWindow = self.user32.SetForegroundWindow
        self.SetForegroundWindow.argtypes = [ctypes.wintypes.HWND]
        self.SetForegroundWindow.restype = ctypes.wintypes.BOOL

        # ShowWindow - Sets window show state (restore, minimize, maximize, etc.)
        self.ShowWindow = self.user32.ShowWindow
        self.ShowWindow.argtypes = [ctypes.wintypes.HWND, ctypes.c_int]
        self.ShowWindow.restype = ctypes.wintypes.BOOL

        # BringWindowToTop - Brings window to top of Z-order without activating
        self.BringWindowToTop = self.user32.BringWindowToTop
        self.BringWindowToTop.argtypes = [ctypes.wintypes.HWND]
        self.BringWindowToTop.restype = ctypes.wintypes.BOOL

        # IsIconic - Determines if window is minimized
        self.IsIconic = self.user32.IsIconic
        self.IsIconic.argtypes = [ctypes.wintypes.HWND]
        self.IsIconic.restype = ctypes.wintypes.BOOL

        # GetForegroundWindow - Retrieves handle to current foreground window
        self.GetForegroundWindow = self.user32.GetForegroundWindow
        self.GetForegroundWindow.argtypes = []
        self.GetForegroundWindow.restype = ctypes.wintypes.HWND

        # GetWindowThreadProcessId - Gets thread and process IDs for a window
        self.GetWindowThreadProcessId = self.user32.GetWindowThreadProcessId
        self.GetWindowThreadProcessId.argtypes = [
            ctypes.wintypes.HWND,
            ctypes.POINTER(ctypes.wintypes.DWORD),
        ]
        self.GetWindowThreadProcessId.restype = ctypes.wintypes.DWORD

        # GetCurrentThreadId - Gets current thread identifier
        self.GetCurrentThreadId = self.kernel32.GetCurrentThreadId
        self.GetCurrentThreadId.argtypes = []
        self.GetCurrentThreadId.restype = ctypes.wintypes.DWORD

        # AttachThreadInput - Attaches/detaches input processing between threads
        self.AttachThreadInput = self.user32.AttachThreadInput
        self.AttachThreadInput.argtypes = [
            ctypes.wintypes.DWORD,
            ctypes.wintypes.DWORD,
            ctypes.wintypes.BOOL,
        ]
        self.AttachThreadInput.restype = ctypes.wintypes.BOOL

        # AllowSetForegroundWindow - Grants permission to set foreground window
        self.AllowSetForegroundWindow = self.user32.AllowSetForegroundWindow
        self.AllowSetForegroundWindow.argtypes = [ctypes.wintypes.DWORD]
        self.AllowSetForegroundWindow.restype = ctypes.wintypes.BOOL

        # GetLastError - Retrieves last-error code value for calling thread
        self.GetLastError = self.kernel32.GetLastError
        self.GetLastError.restype = ctypes.wintypes.DWORD

        # Window show constants
        self.SW_RESTORE = 9  # Restore window to normal size and position
        self.SW_SHOW = 5  # Show window in current size and position
        self.SW_MAXIMIZE = 3  # Maximize window

        # Special process ID for AllowSetForegroundWindow
        self.ASFW_ANY = 0xFFFFFFFF  # Allow any process to set foreground window


# Create a singleton instance for easy access throughout the module
winapi = WindowsAPI()


def focus_window_robust(hwnd: ctypes.wintypes.HWND) -> bool:
    """
    Robustly focus a window using multiple Windows API calls and techniques
    to overcome Windows focus stealing prevention policies.

    This function implements several strategies:
    1. Thread input attachment to bypass focus restrictions
    2. AllowSetForegroundWindow to grant permission
    3. Proper window state restoration
    4. Multiple fallback methods

    Args:
        hwnd: Window handle to focus

    Returns:
        True if focusing was successful, False otherwise
    """
    if not hwnd:
        log.warning("Invalid window handle")
        return False

    try:
        log.debug(f"Attempting to focus window with HWND: {hwnd}")

        # Get the current foreground window and its thread
        current_fg_hwnd = winapi.GetForegroundWindow()
        current_thread_id = winapi.GetCurrentThreadId()

        success = False
        attached_input = False

        try:
            # Strategy 1: Allow any process to set foreground window
            if winapi.AllowSetForegroundWindow(winapi.ASFW_ANY):
                log.debug("Successfully called AllowSetForegroundWindow")
            else:
                log.debug(
                    f"AllowSetForegroundWindow failed, error: {winapi.GetLastError()}"
                )

            # Strategy 2: Thread input attachment if there's a different foreground window
            if current_fg_hwnd and current_fg_hwnd != hwnd:
                fg_process_id = ctypes.wintypes.DWORD()
                fg_thread_id = winapi.GetWindowThreadProcessId(
                    current_fg_hwnd, ctypes.byref(fg_process_id)
                )

                if fg_thread_id and fg_thread_id != current_thread_id:
                    log.debug(
                        f"Attaching thread input: {current_thread_id} -> {fg_thread_id}"
                    )
                    if winapi.AttachThreadInput(current_thread_id, fg_thread_id, True):
                        attached_input = True
                        log.debug("Successfully attached thread input")
                    else:
                        log.debug(
                            f"AttachThreadInput failed, error: {winapi.GetLastError()}"
                        )

            # Strategy 3: Restore window if minimized
            if winapi.IsIconic(hwnd):
                log.debug("Window is minimized, restoring...")
                if winapi.ShowWindow(hwnd, winapi.SW_RESTORE):
                    log.debug("Successfully restored window")
                else:
                    log.debug(
                        f"ShowWindow(SW_RESTORE) failed, error: {winapi.GetLastError()}"
                    )

            # Strategy 4: Attempt to set foreground window
            if winapi.SetForegroundWindow(hwnd):
                log.debug("SetForegroundWindow succeeded")
                success = True
            else:
                error = winapi.GetLastError()
                log.debug(f"SetForegroundWindow failed with error: {error}")

                # Strategy 5: Fallback methods
                log.debug("Trying fallback methods...")

                # Show window and bring to top
                winapi.ShowWindow(hwnd, winapi.SW_SHOW)
                if winapi.BringWindowToTop(hwnd):
                    log.debug("BringWindowToTop succeeded")
                else:
                    log.debug(
                        f"BringWindowToTop failed, error: {winapi.GetLastError()}"
                    )

        finally:
            # Clean up thread input attachment
            if attached_input and current_fg_hwnd:
                fg_process_id = ctypes.wintypes.DWORD()
                fg_thread_id = winapi.GetWindowThreadProcessId(
                    current_fg_hwnd, ctypes.byref(fg_process_id)
                )
                if fg_thread_id:
                    winapi.AttachThreadInput(current_thread_id, fg_thread_id, False)
                    log.debug("Detached thread input")

        log.info(f"Window focus operation completed, success: {success}")
        return success

    except Exception as e:
        log.error(f"Error in robust window focusing: {e}", exc_info=True)
        return False
