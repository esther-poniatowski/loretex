"""
Module: `loretex.utils.logging`

Utility functions for logging messages.

Classes
-------
Logger:
    Simple logger class for logging messages at different levels (info, warning, error).
"""


class Logger:
    """
    Simple logger class for logging messages at different levels.

    Methods
    -------
    info(msg: str)
        Log an informational message.
    warn(msg: str)
        Log a warning message.
    error(msg: str)
        Log an error message.
    """
    def info(self, msg): print(f"[INFO] {msg}")
    def warn(self, msg): print(f"[WARNING] {msg}")
    def error(self, msg): print(f"[ERROR] {msg}")
