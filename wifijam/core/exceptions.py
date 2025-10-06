"""
Custom exceptions for WIFIjam application.
Provides specific error types for better error handling and debugging.
"""


class WIFIjamException(Exception):
    """Base exception for all WIFIjam errors."""
    pass


class AdapterNotFoundError(WIFIjamException):
    """Raised when no suitable WiFi adapter is found."""
    pass


class MonitorModeError(WIFIjamException):
    """Raised when monitor mode operations fail."""
    pass


class PermissionError(WIFIjamException):
    """Raised when insufficient permissions are detected."""
    pass


class NetworkScanError(WIFIjamException):
    """Raised when network scanning fails."""
    pass


class AttackError(WIFIjamException):
    """Raised when attack operations fail."""
    pass


class ConfigurationError(WIFIjamException):
    """Raised when configuration is invalid or missing."""
    pass


class UnsupportedPlatformError(WIFIjamException):
    """Raised when the current platform is not supported for an operation."""
    pass


class InterfaceError(WIFIjamException):
    """Raised when network interface operations fail."""
    pass

