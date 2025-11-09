"""
Network scanning functionality.
Discovers and monitors WiFi networks across different platforms.
"""

import subprocess
import re
import csv
import time
import tempfile
from typing import List, Optional, Dict, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum

from wifijam.core.logger import get_logger
from wifijam.core.system import get_system_detector, OSType
from wifijam.core.exceptions import NetworkScanError
from wifijam.wifi.adapter import WiFiAdapter

logger = get_logger(__name__)

# Pre-compile regex patterns for better performance
BSSID_PATTERN = re.compile(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$')


class SecurityType(Enum):
    """WiFi security types."""
    OPEN = "Open"
    WEP = "WEP"
    WPA = "WPA"
    WPA2 = "WPA2"
    WPA3 = "WPA3"
    WPA_WPA2 = "WPA/WPA2"
    UNKNOWN = "Unknown"


@dataclass
class Network:
    """WiFi network information."""
    ssid: str
    bssid: str
    channel: int
    security: SecurityType
    signal_strength: int
    frequency: Optional[float] = None
    vendor: Optional[str] = None
    clients: int = 0
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "ssid": self.ssid,
            "bssid": self.bssid,
            "channel": self.channel,
            "security": self.security.value,
            "signal": self.signal_strength,
            "frequency": self.frequency,
            "vendor": self.vendor,
            "clients": self.clients,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat()
        }
    
    def update_signal(self, signal: int) -> None:
        """Update signal strength and last seen time."""
        self.signal_strength = signal
        self.last_seen = datetime.now()


class NetworkScanner:
    """Scans for WiFi networks using platform-specific tools."""
    
    def __init__(self, adapter: WiFiAdapter):
        """
        Initialize network scanner.
        
        Args:
            adapter: WiFi adapter to use for scanning
        """
        self.adapter = adapter
        self.system = get_system_detector()
        self.networks: Dict[str, Network] = {}  # BSSID -> Network
        self.is_scanning = False
        self.scan_process: Optional[subprocess.Popen] = None
        self.callback: Optional[Callable[[Network], None]] = None
    
    def start_scan(
        self,
        duration: int = 30,
        channel: Optional[int] = None,
        callback: Optional[Callable[[Network], None]] = None
    ) -> None:
        """
        Start network scanning.
        
        Args:
            duration: Scan duration in seconds (-1 for continuous)
            channel: Specific channel to scan (None for all channels)
            callback: Optional callback function called when new network is discovered
        """
        if self.is_scanning:
            logger.warning("Scan already in progress")
            return
        
        logger.info(f"Starting network scan on {self.adapter.interface}")
        self.is_scanning = True
        self.callback = callback
        
        try:
            if self.system.os_type == OSType.LINUX:
                self._scan_linux(duration, channel)
            elif self.system.os_type == OSType.MACOS:
                self._scan_macos(duration)
            elif self.system.os_type == OSType.WINDOWS:
                self._scan_windows(duration)
            else:
                raise NetworkScanError(f"Scanning not supported on {self.system.os_type.value}")
        
        except Exception as e:
            logger.error(f"Scan error: {e}")
            self.is_scanning = False
            raise NetworkScanError(f"Failed to start scan: {e}")
    
    def _scan_linux(self, duration: int, channel: Optional[int] = None) -> None:
        """Scan networks on Linux using airodump-ng or iw."""
        # Try airodump-ng first (more detailed)
        if self._scan_linux_airodump(duration, channel):
            return
        
        # Fallback to iw scan
        self._scan_linux_iw(duration)
    
    def _scan_linux_airodump(self, duration: int, channel: Optional[int] = None) -> bool:
        """Scan using airodump-ng."""
        try:
            # Create temporary file for output
            temp_dir = tempfile.mkdtemp()
            output_prefix = Path(temp_dir) / "scan"
            
            cmd = [
                "airodump-ng",
                "--write", str(output_prefix),
                "--write-interval", "1",
                "--output-format", "csv"
            ]
            
            if channel:
                cmd.extend(["--channel", str(channel)])
            
            cmd.append(self.adapter.interface)
            
            logger.debug(f"Running: {' '.join(cmd)}")
            
            # Start airodump-ng
            self.scan_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Monitor the CSV file
            csv_file = Path(f"{output_prefix}-01.csv")
            start_time = time.time()
            last_modified = 0
            
            while self.is_scanning:
                if duration > 0 and (time.time() - start_time) >= duration:
                    break
                
                # Only parse if file exists and has been modified
                if csv_file.exists():
                    try:
                        current_modified = csv_file.stat().st_mtime
                        if current_modified > last_modified:
                            self._parse_airodump_csv(csv_file)
                            last_modified = current_modified
                    except OSError:
                        pass  # File might be temporarily unavailable
                
                time.sleep(2)
            
            # Cleanup
            if self.scan_process:
                self.scan_process.terminate()
                self.scan_process.wait(timeout=5)
            
            # Remove temporary files
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return True
        
        except FileNotFoundError:
            logger.warning("airodump-ng not found")
            return False
        except Exception as e:
            logger.error(f"Error in airodump scan: {e}")
            return False
    
    def _parse_airodump_csv(self, csv_file: Path) -> None:
        """Parse airodump-ng CSV output."""
        try:
            # Use buffered reading for better performance
            with open(csv_file, 'r', encoding='utf-8', errors='ignore', buffering=8192) as f:
                content = f.read()
            
            # Split into AP and client sections
            sections = content.split('\n\n')
            if not sections:
                return
            
            # Parse AP section
            lines = sections[0].split('\n')
            if len(lines) < 2:
                return
            
            # Skip header lines - find start of data more efficiently
            data_start = next((i + 1 for i, line in enumerate(lines) 
                             if line.strip().startswith('BSSID')), 0)
            
            # Parse network data
            for line in lines[data_start:]:
                if not line.strip():
                    continue
                
                try:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) < 14:
                        continue
                    
                    bssid = parts[0]
                    if not bssid or not BSSID_PATTERN.match(bssid):
                        continue
                    
                    # Extract network information
                    channel_str = parts[3]
                    channel = int(channel_str) if channel_str.isdigit() else 0
                    
                    signal_str = parts[8]
                    signal = abs(int(signal_str)) if signal_str.lstrip('-').isdigit() else 0
                    
                    security = self._parse_security(parts[5])
                    ssid = parts[13] if len(parts) > 13 else ""
                    
                    # Create or update network
                    if bssid in self.networks:
                        self.networks[bssid].update_signal(signal)
                    else:
                        network = Network(
                            ssid=ssid or f"Hidden_{bssid[-8:]}",
                            bssid=bssid,
                            channel=channel,
                            security=security,
                            signal_strength=signal
                        )
                        self.networks[bssid] = network
                        
                        if self.callback:
                            self.callback(network)
                        
                        logger.info(f"Discovered network: {network.ssid} ({bssid})")
                
                except (ValueError, IndexError) as e:
                    logger.debug(f"Error parsing line: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error parsing airodump CSV: {e}")
    
    def _parse_security(self, security_str: str) -> SecurityType:
        """Parse security type from string."""
        security_str = security_str.upper()
        
        if "WPA3" in security_str:
            return SecurityType.WPA3
        elif "WPA2" in security_str and "WPA" in security_str:
            return SecurityType.WPA_WPA2
        elif "WPA2" in security_str:
            return SecurityType.WPA2
        elif "WPA" in security_str:
            return SecurityType.WPA
        elif "WEP" in security_str:
            return SecurityType.WEP
        elif "OPN" in security_str or not security_str.strip():
            return SecurityType.OPEN
        else:
            return SecurityType.UNKNOWN
    
    def _scan_linux_iw(self, duration: int) -> None:
        """Scan using iw command."""
        logger.info("Scanning with iw command...")
        start_time = time.time()
        scan_interval = 5  # Configurable scan interval
        
        while self.is_scanning:
            if duration > 0 and (time.time() - start_time) >= duration:
                break
            
            try:
                result = subprocess.run(
                    ["iw", self.adapter.interface, "scan"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    self._parse_iw_scan(result.stdout)
            
            except subprocess.TimeoutExpired:
                logger.warning("iw scan timeout")
            except Exception as e:
                logger.error(f"Error in iw scan: {e}")
            
            # Use adaptive sleep based on remaining time
            if duration > 0:
                remaining = duration - (time.time() - start_time)
                sleep_time = min(scan_interval, max(0, remaining))
                if sleep_time > 0:
                    time.sleep(sleep_time)
            else:
                time.sleep(scan_interval)
    
    def _parse_iw_scan(self, output: str) -> None:
        """Parse iw scan output."""
        # Implementation for parsing iw scan output
        # This is a simplified version
        pass
    
    def _scan_macos(self, duration: int) -> None:
        """Scan networks on macOS."""
        logger.info("Scanning on macOS...")
        # macOS scanning implementation
        pass
    
    def _scan_windows(self, duration: int) -> None:
        """Scan networks on Windows."""
        logger.info("Scanning on Windows...")
        # Windows scanning implementation
        pass
    
    def stop_scan(self) -> None:
        """Stop the current scan."""
        logger.info("Stopping network scan")
        self.is_scanning = False
        
        if self.scan_process:
            try:
                self.scan_process.terminate()
                self.scan_process.wait(timeout=5)
            except Exception as e:
                logger.error(f"Error stopping scan process: {e}")
            finally:
                self.scan_process = None
    
    def get_networks(self) -> List[Network]:
        """Get list of discovered networks."""
        return list(self.networks.values())
    
    def get_network(self, bssid: str) -> Optional[Network]:
        """Get network by BSSID."""
        return self.networks.get(bssid)
    
    def clear_networks(self) -> None:
        """Clear discovered networks."""
        self.networks.clear()
        logger.info("Network list cleared")

