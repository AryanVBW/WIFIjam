"""
Device tracking and fingerprinting module.
Tracks WiFi devices and provides comprehensive device information.
"""

import re
import requests
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
from enum import Enum

from wifijam.core.logger import get_logger

logger = get_logger(__name__)


class DeviceType(Enum):
    """Device type classification."""
    UNKNOWN = "unknown"
    SMARTPHONE = "smartphone"
    LAPTOP = "laptop"
    TABLET = "tablet"
    DESKTOP = "desktop"
    IOT = "iot"
    ROUTER = "router"
    ACCESS_POINT = "access_point"
    PRINTER = "printer"
    TV = "tv"
    GAME_CONSOLE = "game_console"
    WEARABLE = "wearable"


@dataclass
class SignalReading:
    """Signal strength reading at a point in time."""
    timestamp: datetime
    signal_strength: int  # dBm
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'signal_strength': self.signal_strength
        }


@dataclass
class ConnectionEvent:
    """Device connection/disconnection event."""
    timestamp: datetime
    event_type: str  # 'connected', 'disconnected', 'roaming'
    bssid: str
    ssid: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'bssid': self.bssid,
            'ssid': self.ssid
        }


@dataclass
class DataTransferStats:
    """Data transfer statistics for a device."""
    bytes_sent: int = 0
    bytes_received: int = 0
    packets_sent: int = 0
    packets_received: int = 0
    last_activity: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'packets_sent': self.packets_sent,
            'packets_received': self.packets_received,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'total_bytes': self.bytes_sent + self.bytes_received,
            'total_packets': self.packets_sent + self.packets_received
        }


@dataclass
class Device:
    """Represents a tracked WiFi device."""
    mac_address: str
    first_seen: datetime
    last_seen: datetime
    vendor: Optional[str] = None
    device_type: DeviceType = DeviceType.UNKNOWN
    device_name: Optional[str] = None
    connected_bssid: Optional[str] = None
    connected_ssid: Optional[str] = None
    signal_history: List[SignalReading] = field(default_factory=list)
    connection_history: List[ConnectionEvent] = field(default_factory=list)
    data_stats: DataTransferStats = field(default_factory=DataTransferStats)
    probe_requests: List[str] = field(default_factory=list)  # SSIDs probed
    capabilities: List[str] = field(default_factory=list)
    operating_system: Optional[str] = None
    is_active: bool = True
    
    def __post_init__(self):
        """Initialize signal history with deque for efficient operations."""
        if not isinstance(self.signal_history, deque):
            self.signal_history = deque(self.signal_history, maxlen=100)
    
    def add_signal_reading(self, signal_strength: int) -> None:
        """Add a signal strength reading."""
        reading = SignalReading(
            timestamp=datetime.now(),
            signal_strength=signal_strength
        )
        self.signal_history.append(reading)
        self.last_seen = datetime.now()
    
    def add_connection_event(self, event_type: str, bssid: str, ssid: Optional[str] = None) -> None:
        """Add a connection event."""
        event = ConnectionEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            bssid=bssid,
            ssid=ssid
        )
        self.connection_history.append(event)
        
        if event_type == 'connected':
            self.connected_bssid = bssid
            self.connected_ssid = ssid
        elif event_type == 'disconnected':
            self.connected_bssid = None
            self.connected_ssid = None
    
    def update_data_stats(self, bytes_sent: int = 0, bytes_received: int = 0,
                         packets_sent: int = 0, packets_received: int = 0) -> None:
        """Update data transfer statistics."""
        self.data_stats.bytes_sent += bytes_sent
        self.data_stats.bytes_received += bytes_received
        self.data_stats.packets_sent += packets_sent
        self.data_stats.packets_received += packets_received
        self.data_stats.last_activity = datetime.now()
        self.last_seen = datetime.now()
    
    def add_probe_request(self, ssid: str) -> None:
        """Add a probed SSID."""
        if ssid and ssid not in self.probe_requests:
            self.probe_requests.append(ssid)
    
    def get_average_signal(self) -> Optional[float]:
        """Get average signal strength."""
        if not self.signal_history:
            return None
        return sum(r.signal_strength for r in self.signal_history) / len(self.signal_history)
    
    def get_current_signal(self) -> Optional[int]:
        """Get most recent signal strength."""
        if not self.signal_history:
            return None
        return self.signal_history[-1].signal_strength
    
    def get_connection_duration(self) -> float:
        """Get total time device has been tracked (in seconds)."""
        return (self.last_seen - self.first_seen).total_seconds()
    
    def is_connected(self) -> bool:
        """Check if device is currently connected to an AP."""
        return self.connected_bssid is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'mac_address': self.mac_address,
            'vendor': self.vendor,
            'device_type': self.device_type.value,
            'device_name': self.device_name,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'connected_bssid': self.connected_bssid,
            'connected_ssid': self.connected_ssid,
            'current_signal': self.get_current_signal(),
            'average_signal': self.get_average_signal(),
            'signal_history': [r.to_dict() for r in list(self.signal_history)[-10:]],  # Last 10
            'connection_history': [e.to_dict() for e in self.connection_history[-10:]],  # Last 10
            'data_stats': self.data_stats.to_dict(),
            'probe_requests': self.probe_requests,
            'capabilities': self.capabilities,
            'operating_system': self.operating_system,
            'is_active': self.is_active,
            'is_connected': self.is_connected(),
            'connection_duration': self.get_connection_duration()
        }


class DeviceTracker:
    """Tracks and manages WiFi devices."""
    
    # MAC OUI database URL
    OUI_API_URL = "https://api.macvendors.com/{}"
    
    def __init__(self):
        """Initialize device tracker."""
        self.devices: Dict[str, Device] = {}
        self._vendor_cache: Dict[str, str] = {}
        logger.info("Device tracker initialized")
    
    def track_device(
        self,
        mac_address: str,
        signal_strength: Optional[int] = None,
        bssid: Optional[str] = None,
        ssid: Optional[str] = None,
        probe_ssid: Optional[str] = None
    ) -> Device:
        """
        Track a device or update existing device information.
        
        Args:
            mac_address: Device MAC address
            signal_strength: Signal strength in dBm
            bssid: Connected BSSID
            ssid: Connected SSID
            probe_ssid: SSID being probed
        
        Returns:
            Device object
        """
        mac_address = mac_address.upper()
        
        # Get or create device
        if mac_address not in self.devices:
            device = Device(
                mac_address=mac_address,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                vendor=self._lookup_vendor(mac_address),
                device_type=self._detect_device_type(mac_address)
            )
            self.devices[mac_address] = device
            logger.info(f"New device tracked: {mac_address} ({device.vendor})")
        else:
            device = self.devices[mac_address]
            device.last_seen = datetime.now()
            device.is_active = True
        
        # Update signal strength
        if signal_strength is not None:
            device.add_signal_reading(signal_strength)
        
        # Update connection info
        if bssid and device.connected_bssid != bssid:
            if device.connected_bssid:
                device.add_connection_event('disconnected', device.connected_bssid)
            device.add_connection_event('connected', bssid, ssid)
        
        # Add probe request
        if probe_ssid:
            device.add_probe_request(probe_ssid)
        
        return device
    
    def get_device(self, mac_address: str) -> Optional[Device]:
        """Get device by MAC address."""
        return self.devices.get(mac_address.upper())
    
    def get_all_devices(self, active_only: bool = False) -> List[Device]:
        """
        Get all tracked devices.
        
        Args:
            active_only: Only return active devices
        
        Returns:
            List of devices
        """
        devices = list(self.devices.values())
        if active_only:
            devices = [d for d in devices if d.is_active]
        return devices
    
    def get_devices_by_bssid(self, bssid: str) -> List[Device]:
        """Get all devices connected to a specific BSSID."""
        return [d for d in self.devices.values() if d.connected_bssid == bssid]
    
    def mark_inactive_devices(self, timeout_seconds: int = 300) -> int:
        """
        Mark devices as inactive if not seen recently.
        
        Args:
            timeout_seconds: Timeout in seconds
        
        Returns:
            Number of devices marked inactive
        """
        now = datetime.now()
        count = 0
        
        for device in self.devices.values():
            if device.is_active:
                time_since_seen = (now - device.last_seen).total_seconds()
                if time_since_seen > timeout_seconds:
                    device.is_active = False
                    count += 1
                    logger.debug(f"Device {device.mac_address} marked inactive")
        
        return count
    
    def _lookup_vendor(self, mac_address: str) -> Optional[str]:
        """
        Lookup vendor from MAC address OUI.
        
        Args:
            mac_address: MAC address
        
        Returns:
            Vendor name or None
        """
        # Check cache first
        oui = mac_address[:8].upper()
        if oui in self._vendor_cache:
            return self._vendor_cache[oui]
        
        try:
            # Try online lookup
            response = requests.get(
                self.OUI_API_URL.format(mac_address),
                timeout=2
            )
            if response.status_code == 200:
                vendor = response.text.strip()
                self._vendor_cache[oui] = vendor
                return vendor
        except Exception as e:
            logger.debug(f"Vendor lookup failed for {mac_address}: {e}")
        
        # Fallback to local OUI database if available
        vendor = self._lookup_vendor_local(oui)
        if vendor:
            self._vendor_cache[oui] = vendor
        
        return vendor
    
    def _lookup_vendor_local(self, oui: str) -> Optional[str]:
        """Lookup vendor from local OUI database."""
        # Common vendors for quick lookup
        common_vendors = {
            '00:50:F2': 'Microsoft',
            '00:0C:29': 'VMware',
            '08:00:27': 'VirtualBox',
            'DC:A6:32': 'Raspberry Pi',
            'B8:27:EB': 'Raspberry Pi',
            '00:1B:63': 'Apple',
            '00:03:93': 'Apple',
            '00:0A:95': 'Apple',
            '00:17:F2': 'Apple',
            '00:1C:B3': 'Apple',
            '00:1E:C2': 'Apple',
            '00:21:E9': 'Apple',
            '00:23:12': 'Apple',
            '00:23:32': 'Apple',
            '00:23:6C': 'Apple',
            '00:23:DF': 'Apple',
            '00:24:36': 'Apple',
            '00:25:00': 'Apple',
            '00:25:4B': 'Apple',
            '00:25:BC': 'Apple',
            '00:26:08': 'Apple',
            '00:26:4A': 'Apple',
            '00:26:B0': 'Apple',
            '00:26:BB': 'Apple',
        }
        return common_vendors.get(oui)
    
    def _detect_device_type(self, mac_address: str) -> DeviceType:
        """
        Detect device type from MAC address and vendor.
        
        Args:
            mac_address: MAC address
        
        Returns:
            Device type
        """
        vendor = self._lookup_vendor(mac_address)
        if not vendor:
            return DeviceType.UNKNOWN
        
        vendor_lower = vendor.lower()
        
        # Device type detection based on vendor
        if 'apple' in vendor_lower or 'iphone' in vendor_lower:
            return DeviceType.SMARTPHONE
        elif 'samsung' in vendor_lower:
            return DeviceType.SMARTPHONE
        elif 'raspberry' in vendor_lower:
            return DeviceType.IOT
        elif 'router' in vendor_lower or 'cisco' in vendor_lower:
            return DeviceType.ROUTER
        elif 'access point' in vendor_lower or 'ubiquiti' in vendor_lower:
            return DeviceType.ACCESS_POINT
        elif 'printer' in vendor_lower or 'hp' in vendor_lower or 'canon' in vendor_lower:
            return DeviceType.PRINTER
        elif 'tv' in vendor_lower or 'television' in vendor_lower:
            return DeviceType.TV
        elif 'xbox' in vendor_lower or 'playstation' in vendor_lower or 'nintendo' in vendor_lower:
            return DeviceType.GAME_CONSOLE
        
        return DeviceType.UNKNOWN
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tracker statistics."""
        active_devices = [d for d in self.devices.values() if d.is_active]
        connected_devices = [d for d in active_devices if d.is_connected()]
        
        device_types = {}
        for device in active_devices:
            device_type = device.device_type.value
            device_types[device_type] = device_types.get(device_type, 0) + 1
        
        return {
            'total_devices': len(self.devices),
            'active_devices': len(active_devices),
            'connected_devices': len(connected_devices),
            'device_types': device_types,
            'vendors': len(self._vendor_cache)
        }

