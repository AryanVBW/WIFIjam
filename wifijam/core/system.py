"""
System detection and information module.
Provides cross-platform system information and capability detection.
"""

import platform
import subprocess
import os
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from wifijam.core.logger import get_logger
from wifijam.core.exceptions import UnsupportedPlatformError, PermissionError

logger = get_logger(__name__)


class OSType(Enum):
    """Supported operating system types."""
    LINUX = "linux"
    MACOS = "darwin"
    WINDOWS = "windows"
    UNKNOWN = "unknown"


@dataclass
class SystemInfo:
    """System information data class."""
    os_type: OSType
    os_name: str
    os_version: str
    architecture: str
    hostname: str
    python_version: str
    is_root: bool
    has_monitor_mode_support: bool
    has_packet_injection_support: bool


class SystemDetector:
    """Detects and provides system information."""
    
    def __init__(self):
        """Initialize system detector."""
        self.os_type = self._detect_os_type()
        self.system_info = self._gather_system_info()
    
    def _detect_os_type(self) -> OSType:
        """Detect the operating system type."""
        system = platform.system().lower()
        
        if system == "linux":
            return OSType.LINUX
        elif system == "darwin":
            return OSType.MACOS
        elif system == "windows":
            return OSType.WINDOWS
        else:
            return OSType.UNKNOWN
    
    def _gather_system_info(self) -> SystemInfo:
        """Gather comprehensive system information."""
        try:
            os_name = platform.system()
            os_version = platform.release()
            architecture = platform.machine()
            hostname = platform.node()
            python_version = platform.python_version()
            
            # Check if running as root/admin
            is_root = self._check_root_privileges()
            
            # Check monitor mode and packet injection support
            has_monitor_mode = self._check_monitor_mode_support()
            has_packet_injection = self._check_packet_injection_support()
            
            return SystemInfo(
                os_type=self.os_type,
                os_name=os_name,
                os_version=os_version,
                architecture=architecture,
                hostname=hostname,
                python_version=python_version,
                is_root=is_root,
                has_monitor_mode_support=has_monitor_mode,
                has_packet_injection_support=has_packet_injection
            )
        
        except Exception as e:
            logger.error(f"Failed to gather system information: {e}")
            raise
    
    def _check_root_privileges(self) -> bool:
        """Check if running with root/administrator privileges."""
        try:
            if self.os_type == OSType.WINDOWS:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception as e:
            logger.warning(f"Failed to check root privileges: {e}")
            return False
    
    def _check_monitor_mode_support(self) -> bool:
        """Check if the system supports monitor mode."""
        if self.os_type == OSType.LINUX:
            # Check if iw or iwconfig is available
            try:
                subprocess.run(
                    ["which", "iw"],
                    capture_output=True,
                    check=True,
                    timeout=5
                )
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                try:
                    subprocess.run(
                        ["which", "iwconfig"],
                        capture_output=True,
                        check=True,
                        timeout=5
                    )
                    return True
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                    return False
        
        elif self.os_type == OSType.MACOS:
            # macOS has limited support, only with specific adapters
            return False
        
        elif self.os_type == OSType.WINDOWS:
            # Windows doesn't support monitor mode natively
            return False
        
        return False
    
    def _check_packet_injection_support(self) -> bool:
        """Check if the system supports packet injection."""
        if self.os_type == OSType.LINUX:
            # Check if aircrack-ng suite is available
            try:
                subprocess.run(
                    ["which", "aireplay-ng"],
                    capture_output=True,
                    check=True,
                    timeout=5
                )
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                return False
        
        # macOS and Windows have very limited support
        return False
    
    def get_linux_distribution(self) -> Optional[str]:
        """Get Linux distribution name."""
        if self.os_type != OSType.LINUX:
            return None
        
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("ID="):
                        return line.split("=")[1].strip().strip('"')
        except Exception as e:
            logger.warning(f"Failed to detect Linux distribution: {e}")
        
        return None
    
    def check_dependencies(self) -> Dict[str, bool]:
        """
        Check if required system dependencies are installed.
        
        Returns:
            Dictionary mapping dependency names to availability status
        """
        dependencies = {}
        
        if self.os_type == OSType.LINUX:
            # Check Linux-specific tools
            tools = ["iw", "iwconfig", "airmon-ng", "airodump-ng", "aireplay-ng", "ip"]
            for tool in tools:
                try:
                    result = subprocess.run(
                        ["which", tool],
                        capture_output=True,
                        timeout=5
                    )
                    dependencies[tool] = result.returncode == 0
                except Exception:
                    dependencies[tool] = False
        
        elif self.os_type == OSType.MACOS:
            # Check macOS-specific tools
            airport_path = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
            dependencies["airport"] = os.path.exists(airport_path)
            dependencies["networksetup"] = True  # Built-in command
        
        elif self.os_type == OSType.WINDOWS:
            # Check Windows-specific tools
            dependencies["netsh"] = True  # Built-in command
        
        return dependencies
    
    def get_info_dict(self) -> Dict:
        """Get system information as dictionary."""
        return {
            "os_type": self.system_info.os_type.value,
            "os_name": self.system_info.os_name,
            "os_version": self.system_info.os_version,
            "architecture": self.system_info.architecture,
            "hostname": self.system_info.hostname,
            "python_version": self.system_info.python_version,
            "is_root": self.system_info.is_root,
            "has_monitor_mode_support": self.system_info.has_monitor_mode_support,
            "has_packet_injection_support": self.system_info.has_packet_injection_support,
            "dependencies": self.check_dependencies()
        }
    
    def require_root(self) -> None:
        """Raise exception if not running as root."""
        if not self.system_info.is_root:
            raise PermissionError(
                "This operation requires root/administrator privileges. "
                "Please run with sudo (Linux/macOS) or as Administrator (Windows)."
            )
    
    def require_linux(self) -> None:
        """Raise exception if not running on Linux."""
        if self.os_type != OSType.LINUX:
            raise UnsupportedPlatformError(
                f"This operation is only supported on Linux. Current OS: {self.os_type.value}"
            )


# Global system detector instance
_system_detector: Optional[SystemDetector] = None


def get_system_detector() -> SystemDetector:
    """Get or create global system detector instance."""
    global _system_detector
    if _system_detector is None:
        _system_detector = SystemDetector()
    return _system_detector

