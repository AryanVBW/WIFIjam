"""
WIFIjam - Professional WiFi Security Testing Tool
A comprehensive, cross-platform WiFi monitoring and security testing application.

Author: Vivek W (AryanVBW)
License: MIT
Version: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "Vivek W (AryanVBW)"
__license__ = "MIT"
__email__ = "admin@aryanvbw.live"

from wifijam.core.logger import get_logger
from wifijam.core.config import Config

# Initialize default logger
logger = get_logger(__name__)

# Package metadata
__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "logger",
    "Config",
]

