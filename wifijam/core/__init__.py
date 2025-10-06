"""
Core module for WIFIjam
Contains fundamental utilities, configuration, and logging.
"""

from wifijam.core.logger import get_logger, setup_logging
from wifijam.core.config import Config
from wifijam.core.exceptions import (
    WIFIjamException,
    AdapterNotFoundError,
    MonitorModeError,
    PermissionError as WIFIjamPermissionError,
    NetworkScanError,
    AttackError,
)

__all__ = [
    "get_logger",
    "setup_logging",
    "Config",
    "WIFIjamException",
    "AdapterNotFoundError",
    "MonitorModeError",
    "WIFIjamPermissionError",
    "NetworkScanError",
    "AttackError",
]

