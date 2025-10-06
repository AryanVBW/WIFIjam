"""
WiFi adapter detection and management.
Provides cross-platform WiFi adapter enumeration and information.
"""

import subprocess
import re
from typing import List, Optional, Dict
from dataclasses import dataclass
from enum import Enum

from wifijam.core.logger import get_logger
from wifijam.core.system import get_system_detector, OSType
from wifijam.core.exceptions import AdapterNotFoundError, InterfaceError

logger = get_logger(__name__)


class AdapterCapability(Enum):
    """WiFi adapter capabilities."""
    MONITOR_MODE = "monitor_mode"
    PACKET_INJECTION = "packet_injection"
    DUAL_BAND = "dual_band"
    CHANNEL_HOPPING = "channel_hopping"


@dataclass
class WiFiAdapter:
    """WiFi adapter information."""
    interface: str
    name: str
    mac_address: Optional[str] = None
    driver: Optional[str] = None
    chipset: Optional[str] = None
    is_monitor_mode: bool = False
    is_up: bool = False
    capabilities: List[AdapterCapability] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "interface": self.interface,
            "name": self.name,
            "mac_address": self.mac_address,
            "driver": self.driver,
            "chipset": self.chipset,
            "is_monitor_mode": self.is_monitor_mode,
            "is_up": self.is_up,
            "capabilities": [cap.value for cap in self.capabilities]
        }


class AdapterManager:
    """Manages WiFi adapter detection and operations."""
    
    def __init__(self):
        """Initialize adapter manager."""
        self.system = get_system_detector()
        self.adapters: List[WiFiAdapter] = []
        self.refresh()
    
    def refresh(self) -> None:
        """Refresh the list of available adapters."""
        logger.info("Refreshing WiFi adapter list...")
        
        if self.system.os_type == OSType.LINUX:
            self.adapters = self._detect_linux_adapters()
        elif self.system.os_type == OSType.MACOS:
            self.adapters = self._detect_macos_adapters()
        elif self.system.os_type == OSType.WINDOWS:
            self.adapters = self._detect_windows_adapters()
        else:
            logger.warning(f"Unsupported OS: {self.system.os_type}")
            self.adapters = []
        
        logger.info(f"Found {len(self.adapters)} WiFi adapter(s)")
    
    def _detect_linux_adapters(self) -> List[WiFiAdapter]:
        """Detect WiFi adapters on Linux."""
        adapters = []
        
        try:
            # Use iw dev to list wireless interfaces
            result = subprocess.run(
                ["iw", "dev"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse iw dev output
                interface_pattern = re.compile(r'Interface\s+(\S+)')
                mac_pattern = re.compile(r'addr\s+([0-9a-fA-F:]{17})')
                type_pattern = re.compile(r'type\s+(\S+)')
                
                current_interface = None
                current_mac = None
                current_type = None
                
                for line in result.stdout.split('\n'):
                    interface_match = interface_pattern.search(line)
                    if interface_match:
                        if current_interface:
                            # Save previous adapter
                            adapter = self._create_linux_adapter(
                                current_interface,
                                current_mac,
                                current_type
                            )
                            if adapter:
                                adapters.append(adapter)
                        
                        current_interface = interface_match.group(1)
                        current_mac = None
                        current_type = None
                    
                    mac_match = mac_pattern.search(line)
                    if mac_match:
                        current_mac = mac_match.group(1)
                    
                    type_match = type_pattern.search(line)
                    if type_match:
                        current_type = type_match.group(1)
                
                # Don't forget the last adapter
                if current_interface:
                    adapter = self._create_linux_adapter(
                        current_interface,
                        current_mac,
                        current_type
                    )
                    if adapter:
                        adapters.append(adapter)
        
        except subprocess.TimeoutExpired:
            logger.error("Timeout while detecting Linux adapters")
        except FileNotFoundError:
            logger.warning("iw command not found. Trying iwconfig...")
            adapters = self._detect_linux_adapters_iwconfig()
        except Exception as e:
            logger.error(f"Error detecting Linux adapters: {e}")
        
        return adapters
    
    def _detect_linux_adapters_iwconfig(self) -> List[WiFiAdapter]:
        """Fallback: Detect adapters using iwconfig."""
        adapters = []
        
        try:
            result = subprocess.run(
                ["iwconfig"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse iwconfig output
                for line in result.stdout.split('\n'):
                    if 'IEEE 802.11' in line or 'ESSID' in line:
                        interface = line.split()[0]
                        if interface and not interface.startswith(' '):
                            adapter = WiFiAdapter(
                                interface=interface,
                                name=f"WiFi Adapter ({interface})",
                                is_up=True
                            )
                            adapters.append(adapter)
        
        except Exception as e:
            logger.error(f"Error detecting adapters with iwconfig: {e}")
        
        return adapters
    
    def _create_linux_adapter(
        self,
        interface: str,
        mac: Optional[str],
        iface_type: Optional[str]
    ) -> Optional[WiFiAdapter]:
        """Create WiFiAdapter object for Linux interface."""
        try:
            # Get additional info
            driver = self._get_linux_driver(interface)
            is_up = self._check_interface_up(interface)
            is_monitor = iface_type == "monitor" if iface_type else False
            
            # Determine capabilities
            capabilities = []
            if is_monitor or self._check_monitor_capability(interface):
                capabilities.append(AdapterCapability.MONITOR_MODE)
            
            adapter = WiFiAdapter(
                interface=interface,
                name=f"WiFi Adapter ({interface})",
                mac_address=mac,
                driver=driver,
                is_monitor_mode=is_monitor,
                is_up=is_up,
                capabilities=capabilities
            )
            
            return adapter
        
        except Exception as e:
            logger.warning(f"Failed to create adapter for {interface}: {e}")
            return None
    
    def _get_linux_driver(self, interface: str) -> Optional[str]:
        """Get driver name for Linux interface."""
        try:
            driver_path = f"/sys/class/net/{interface}/device/driver"
            if subprocess.run(["test", "-L", driver_path], capture_output=True).returncode == 0:
                result = subprocess.run(
                    ["readlink", driver_path],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.strip().split('/')[-1]
        except Exception:
            pass
        return None
    
    def _check_interface_up(self, interface: str) -> bool:
        """Check if interface is up."""
        try:
            result = subprocess.run(
                ["ip", "link", "show", interface],
                capture_output=True,
                text=True,
                timeout=5
            )
            return "UP" in result.stdout
        except Exception:
            return False
    
    def _check_monitor_capability(self, interface: str) -> bool:
        """Check if interface supports monitor mode."""
        try:
            result = subprocess.run(
                ["iw", interface, "info"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return "monitor" in result.stdout.lower()
        except Exception:
            return False
    
    def _detect_macos_adapters(self) -> List[WiFiAdapter]:
        """Detect WiFi adapters on macOS."""
        adapters = []
        
        try:
            # Use networksetup to list network services
            result = subprocess.run(
                ["networksetup", "-listallhardwareports"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                current_name = None
                
                for line in lines:
                    if line.startswith('Hardware Port:'):
                        current_name = line.split(':', 1)[1].strip()
                    elif line.startswith('Device:') and current_name:
                        if 'Wi-Fi' in current_name or 'AirPort' in current_name:
                            interface = line.split(':', 1)[1].strip()
                            adapter = WiFiAdapter(
                                interface=interface,
                                name=current_name,
                                is_up=True
                            )
                            adapters.append(adapter)
                        current_name = None
        
        except Exception as e:
            logger.error(f"Error detecting macOS adapters: {e}")
        
        return adapters
    
    def _detect_windows_adapters(self) -> List[WiFiAdapter]:
        """Detect WiFi adapters on Windows."""
        adapters = []
        
        try:
            # Use netsh to list wireless interfaces
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse netsh output
                name_pattern = re.compile(r'Name\s+:\s+(.+)')
                
                for line in result.stdout.split('\n'):
                    name_match = name_pattern.search(line)
                    if name_match:
                        name = name_match.group(1).strip()
                        adapter = WiFiAdapter(
                            interface=name,
                            name=name,
                            is_up=True
                        )
                        adapters.append(adapter)
        
        except Exception as e:
            logger.error(f"Error detecting Windows adapters: {e}")
        
        return adapters
    
    def get_adapter(self, interface: str) -> Optional[WiFiAdapter]:
        """Get adapter by interface name."""
        for adapter in self.adapters:
            if adapter.interface == interface:
                return adapter
        return None
    
    def get_monitor_capable_adapters(self) -> List[WiFiAdapter]:
        """Get list of adapters capable of monitor mode."""
        return [
            adapter for adapter in self.adapters
            if AdapterCapability.MONITOR_MODE in adapter.capabilities
        ]
    
    def get_default_adapter(self) -> Optional[WiFiAdapter]:
        """Get the default/first available adapter."""
        return self.adapters[0] if self.adapters else None
    
    def to_dict_list(self) -> List[Dict]:
        """Convert all adapters to list of dictionaries."""
        return [adapter.to_dict() for adapter in self.adapters]

