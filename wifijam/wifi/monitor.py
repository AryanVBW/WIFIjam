"""
Monitor mode management for WiFi adapters.
Handles enabling/disabling monitor mode on supported adapters.
"""

import subprocess
import time
from typing import Optional

from wifijam.core.logger import get_logger
from wifijam.core.system import get_system_detector, OSType
from wifijam.core.exceptions import MonitorModeError, UnsupportedPlatformError, PermissionError
from wifijam.wifi.adapter import WiFiAdapter

logger = get_logger(__name__)


class MonitorMode:
    """Manages monitor mode operations for WiFi adapters."""
    
    def __init__(self, adapter: WiFiAdapter):
        """
        Initialize monitor mode manager.
        
        Args:
            adapter: WiFi adapter to manage
        """
        self.adapter = adapter
        self.system = get_system_detector()
        self.original_mode = None
    
    def enable(self) -> bool:
        """
        Enable monitor mode on the adapter.
        
        Returns:
            True if successful, False otherwise
        
        Raises:
            UnsupportedPlatformError: If platform doesn't support monitor mode
            PermissionError: If insufficient privileges
            MonitorModeError: If monitor mode cannot be enabled
        """
        logger.info(f"Enabling monitor mode on {self.adapter.interface}")
        
        # Check if already in monitor mode
        if self.adapter.is_monitor_mode:
            logger.info(f"{self.adapter.interface} is already in monitor mode")
            return True
        
        # Check platform support
        if self.system.os_type != OSType.LINUX:
            raise UnsupportedPlatformError(
                f"Monitor mode is not supported on {self.system.os_type.value}"
            )
        
        # Check root privileges
        if not self.system.system_info.is_root:
            raise PermissionError(
                "Root privileges required to enable monitor mode. Run with sudo."
            )
        
        try:
            # Method 1: Try using iw
            if self._enable_with_iw():
                self.adapter.is_monitor_mode = True
                logger.info(f"Monitor mode enabled on {self.adapter.interface}")
                return True
            
            # Method 2: Try using airmon-ng
            if self._enable_with_airmon():
                self.adapter.is_monitor_mode = True
                logger.info(f"Monitor mode enabled on {self.adapter.interface}")
                return True
            
            raise MonitorModeError(
                f"Failed to enable monitor mode on {self.adapter.interface}"
            )
        
        except Exception as e:
            logger.error(f"Error enabling monitor mode: {e}")
            raise MonitorModeError(f"Failed to enable monitor mode: {e}")
    
    def _enable_with_iw(self) -> bool:
        """Enable monitor mode using iw command."""
        try:
            interface = self.adapter.interface
            
            # Bring interface down
            subprocess.run(
                ["ip", "link", "set", interface, "down"],
                check=True,
                capture_output=True,
                timeout=10
            )
            
            # Kill conflicting processes
            try:
                subprocess.run(
                    ["airmon-ng", "check", "kill"],
                    capture_output=True,
                    timeout=10
                )
            except (FileNotFoundError, subprocess.CalledProcessError):
                logger.warning("airmon-ng not available for killing processes")
            
            # Set monitor mode
            subprocess.run(
                ["iw", interface, "set", "monitor", "control"],
                check=True,
                capture_output=True,
                timeout=10
            )
            
            # Bring interface up
            subprocess.run(
                ["ip", "link", "set", interface, "up"],
                check=True,
                capture_output=True,
                timeout=10
            )
            
            # Verify monitor mode
            time.sleep(1)
            result = subprocess.run(
                ["iw", interface, "info"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return "type monitor" in result.stdout.lower()
        
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to enable monitor mode with iw: {e}")
            return False
        except Exception as e:
            logger.warning(f"Error in _enable_with_iw: {e}")
            return False
    
    def _enable_with_airmon(self) -> bool:
        """Enable monitor mode using airmon-ng."""
        try:
            interface = self.adapter.interface
            
            # Kill conflicting processes
            subprocess.run(
                ["airmon-ng", "check", "kill"],
                capture_output=True,
                timeout=10
            )
            
            # Start monitor mode
            result = subprocess.run(
                ["airmon-ng", "start", interface],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                # airmon-ng typically creates interface with 'mon' suffix
                # Update adapter interface name if changed
                if f"{interface}mon" in result.stdout:
                    self.adapter.interface = f"{interface}mon"
                    logger.info(f"Interface renamed to {self.adapter.interface}")
                
                return True
            
            return False
        
        except FileNotFoundError:
            logger.warning("airmon-ng not found")
            return False
        except Exception as e:
            logger.warning(f"Error in _enable_with_airmon: {e}")
            return False
    
    def disable(self) -> bool:
        """
        Disable monitor mode and restore managed mode.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Disabling monitor mode on {self.adapter.interface}")
        
        if not self.adapter.is_monitor_mode:
            logger.info(f"{self.adapter.interface} is not in monitor mode")
            return True
        
        if self.system.os_type != OSType.LINUX:
            logger.warning(f"Monitor mode operations not supported on {self.system.os_type.value}")
            return False
        
        try:
            # Method 1: Try using iw
            if self._disable_with_iw():
                self.adapter.is_monitor_mode = False
                logger.info(f"Monitor mode disabled on {self.adapter.interface}")
                return True
            
            # Method 2: Try using airmon-ng
            if self._disable_with_airmon():
                self.adapter.is_monitor_mode = False
                logger.info(f"Monitor mode disabled on {self.adapter.interface}")
                return True
            
            logger.warning(f"Failed to disable monitor mode on {self.adapter.interface}")
            return False
        
        except Exception as e:
            logger.error(f"Error disabling monitor mode: {e}")
            return False
    
    def _disable_with_iw(self) -> bool:
        """Disable monitor mode using iw command."""
        try:
            interface = self.adapter.interface
            
            # Bring interface down
            subprocess.run(
                ["ip", "link", "set", interface, "down"],
                check=True,
                capture_output=True,
                timeout=10
            )
            
            # Set managed mode
            subprocess.run(
                ["iw", interface, "set", "type", "managed"],
                check=True,
                capture_output=True,
                timeout=10
            )
            
            # Bring interface up
            subprocess.run(
                ["ip", "link", "set", interface, "up"],
                check=True,
                capture_output=True,
                timeout=10
            )
            
            # Restart NetworkManager if available
            try:
                subprocess.run(
                    ["systemctl", "restart", "NetworkManager"],
                    capture_output=True,
                    timeout=10
                )
            except Exception:
                pass
            
            return True
        
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to disable monitor mode with iw: {e}")
            return False
        except Exception as e:
            logger.warning(f"Error in _disable_with_iw: {e}")
            return False
    
    def _disable_with_airmon(self) -> bool:
        """Disable monitor mode using airmon-ng."""
        try:
            interface = self.adapter.interface
            
            # Stop monitor mode
            result = subprocess.run(
                ["airmon-ng", "stop", interface],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                # Restore original interface name if it was changed
                if interface.endswith("mon"):
                    self.adapter.interface = interface[:-3]
                    logger.info(f"Interface restored to {self.adapter.interface}")
                
                # Restart NetworkManager
                try:
                    subprocess.run(
                        ["systemctl", "restart", "NetworkManager"],
                        capture_output=True,
                        timeout=10
                    )
                except Exception:
                    pass
                
                return True
            
            return False
        
        except FileNotFoundError:
            logger.warning("airmon-ng not found")
            return False
        except Exception as e:
            logger.warning(f"Error in _disable_with_airmon: {e}")
            return False
    
    def is_enabled(self) -> bool:
        """Check if monitor mode is currently enabled."""
        return self.adapter.is_monitor_mode

