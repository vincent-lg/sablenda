"""Inter-process communication using Windows named pipes."""

import json
import logging
import threading
import time
from typing import Callable

import win32file
import win32pipe
import pywintypes

log = logging.getLogger(__name__)

# Use a consistent pipe name based on application
PIPE_NAME = r"\\.\pipe\Sablenda_InstanceManager"
PIPE_TIMEOUT = 5000  # milliseconds
CONNECT_TIMEOUT = 2000  # milliseconds


class NamedPipeServer:
    """Server for receiving commands from other instances via named pipe."""

    def __init__(self, callback: Callable[[dict], None]):
        """
        Initialize the named pipe server.

        Args:
            callback: Function to call when a command is received.
                     Will be called with a dict containing the command data.
        """
        self.callback = callback
        self.pipe_handle = None
        self.monitoring = False
        self.monitor_thread: threading.Thread | None = None
        self.stop_event = threading.Event()

    def start(self) -> None:
        """Start the named pipe server in a background thread."""
        if self.monitoring:
            log.warning("Named pipe server already running")
            return

        self.monitoring = True
        self.stop_event.clear()
        self.monitor_thread = threading.Thread(target=self._monitor_pipe, daemon=True)
        self.monitor_thread.start()
        log.debug("Named pipe server started")

    def stop(self) -> None:
        """Stop the named pipe server."""
        if not self.monitoring:
            return

        self.monitoring = False
        self.stop_event.set()

        if self.pipe_handle:
            try:
                win32file.CloseHandle(self.pipe_handle)
            except Exception as e:
                log.debug(f"Error closing pipe handle: {e}")
            self.pipe_handle = None

        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
            self.monitor_thread = None

        log.debug("Named pipe server stopped")

    def _monitor_pipe(self) -> None:
        """Monitor the named pipe for incoming commands."""
        log.info(f"Pipe monitor thread started, listening on: {PIPE_NAME}")
        while self.monitoring and not self.stop_event.is_set():
            try:
                # Create the named pipe
                log.debug("Creating named pipe...")
                self.pipe_handle = win32pipe.CreateNamedPipe(
                    PIPE_NAME,
                    win32pipe.PIPE_ACCESS_INBOUND,
                    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                    win32pipe.PIPE_UNLIMITED_INSTANCES,
                    4096,  # output buffer size
                    4096,  # input buffer size
                    PIPE_TIMEOUT,
                    None  # security attributes
                )

                log.debug("Named pipe created, waiting for client connections...")

                # Wait for a client to connect
                win32pipe.ConnectNamedPipe(self.pipe_handle, None)
                log.info("Client connected to named pipe")

                # Read the command
                try:
                    data = win32file.ReadFile(self.pipe_handle, 4096)[1]
                    if data:
                        command = json.loads(data.decode('utf-8'))
                        log.info(f"Pipe server received command: {command.get('action', 'unknown')}")
                        self.callback(command)
                    else:
                        log.debug("Received empty data from pipe")
                except json.JSONDecodeError as e:
                    log.error(f"Failed to parse command from pipe: {e}")
                except Exception as e:
                    log.error(f"Error reading from pipe: {e}")
                finally:
                    try:
                        win32file.CloseHandle(self.pipe_handle)
                    except Exception:
                        pass
                    self.pipe_handle = None

            except pywintypes.error as e:
                if self.stop_event.is_set():
                    log.debug("Stop event set, exiting pipe monitor")
                    break
                log.debug(f"Pipe error (will retry): {e}")
                time.sleep(0.1)
            except Exception as e:
                if self.stop_event.is_set():
                    log.debug("Stop event set, exiting pipe monitor")
                    break
                log.error(f"Unexpected error in pipe monitor: {e}")
                time.sleep(0.5)

        log.info("Pipe monitor thread stopped")


class NamedPipeClient:
    """Client for sending commands to the main instance via named pipe."""

    @staticmethod
    def send_command(action: str, **kwargs) -> bool:
        """
        Send a command to the main instance.

        Args:
            action: The action to perform (e.g., "focus")
            **kwargs: Additional arguments to include in the command

        Returns:
            True if command was sent successfully, False otherwise
        """
        command = {"action": action}
        command.update(kwargs)

        try:
            log.debug(f"Attempting to connect to pipe: {PIPE_NAME}")

            # Try to open the pipe
            pipe_handle = win32file.CreateFile(
                PIPE_NAME,
                win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )

            log.debug(f"Connected to pipe, sending command: {action}")

            # Send the command
            command_json = json.dumps(command).encode('utf-8')
            win32file.WriteFile(pipe_handle, command_json)
            win32file.CloseHandle(pipe_handle)

            log.debug(f"Command sent successfully: {action}")
            return True

        except pywintypes.error as e:
            log.debug(f"Pipe connection failed (pipe may not exist or not ready): error code {e.args[0]}")
            return False
        except Exception as e:
            log.error(f"Error sending command: {e}")
            return False
