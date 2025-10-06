"""
Packet capture and analysis module.
Captures WiFi packets and provides analysis capabilities.
"""

import os
import time
import subprocess
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

try:
    from scapy.all import (
        Dot11, Dot11Beacon, Dot11ProbeReq, Dot11ProbeResp,
        Dot11Auth, Dot11Deauth, Dot11Disas, Dot11AssoReq,
        Dot11AssoResp, Dot11ReassoReq, Dot11ReassoResp,
        RadioTap, EAPOL, sniff, wrpcap, rdpcap
    )
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

from wifijam.core.logger import get_logger
from wifijam.core.exceptions import WIFIjamException
from wifijam.wifi.adapter import WiFiAdapter

logger = get_logger(__name__)


class CaptureError(WIFIjamException):
    """Packet capture error."""
    pass


@dataclass
class PacketStats:
    """Packet capture statistics."""
    total_packets: int = 0
    beacon_frames: int = 0
    probe_requests: int = 0
    probe_responses: int = 0
    auth_frames: int = 0
    deauth_frames: int = 0
    disassoc_frames: int = 0
    data_frames: int = 0
    eapol_frames: int = 0
    management_frames: int = 0
    control_frames: int = 0
    data_bytes: int = 0
    capture_duration: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_packets': self.total_packets,
            'beacon_frames': self.beacon_frames,
            'probe_requests': self.probe_requests,
            'probe_responses': self.probe_responses,
            'auth_frames': self.auth_frames,
            'deauth_frames': self.deauth_frames,
            'disassoc_frames': self.disassoc_frames,
            'data_frames': self.data_frames,
            'eapol_frames': self.eapol_frames,
            'management_frames': self.management_frames,
            'control_frames': self.control_frames,
            'data_bytes': self.data_bytes,
            'capture_duration': self.capture_duration,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
        }


@dataclass
class CapturedPacket:
    """Represents a captured packet."""
    timestamp: datetime
    packet_type: str
    source_mac: Optional[str]
    dest_mac: Optional[str]
    bssid: Optional[str]
    ssid: Optional[str]
    channel: Optional[int]
    signal_strength: Optional[int]
    packet_size: int
    raw_data: Optional[bytes] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'packet_type': self.packet_type,
            'source_mac': self.source_mac,
            'dest_mac': self.dest_mac,
            'bssid': self.bssid,
            'ssid': self.ssid,
            'channel': self.channel,
            'signal_strength': self.signal_strength,
            'packet_size': self.packet_size,
        }


class PacketCapture:
    """Manages packet capture operations."""
    
    def __init__(self, adapter: WiFiAdapter, output_dir: Optional[Path] = None):
        """
        Initialize packet capture.
        
        Args:
            adapter: WiFi adapter to capture on
            output_dir: Directory to save capture files
        """
        if not SCAPY_AVAILABLE:
            raise CaptureError("Scapy is required for packet capture")
        
        self.adapter = adapter
        self.output_dir = output_dir or Path.home() / ".wifijam" / "captures"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.is_capturing = False
        self.packets: List[CapturedPacket] = []
        self.stats = PacketStats()
        self.capture_file: Optional[Path] = None
        self.handshakes: Dict[str, List[Any]] = defaultdict(list)
        
        logger.info(f"Packet capture initialized on {adapter.interface}")
    
    def start_capture(
        self,
        duration: Optional[int] = None,
        packet_count: Optional[int] = None,
        filter_bssid: Optional[str] = None,
        capture_handshakes: bool = False,
        callback: Optional[Callable[[CapturedPacket], None]] = None
    ) -> Path:
        """
        Start packet capture.
        
        Args:
            duration: Capture duration in seconds (None for continuous)
            packet_count: Stop after capturing this many packets
            filter_bssid: Only capture packets from this BSSID
            capture_handshakes: Focus on capturing WPA handshakes
            callback: Callback function for each captured packet
        
        Returns:
            Path to capture file
        """
        if self.is_capturing:
            raise CaptureError("Capture already in progress")
        
        # Generate capture filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.capture_file = self.output_dir / f"capture_{timestamp}.pcap"
        
        self.is_capturing = True
        self.packets.clear()
        self.stats = PacketStats(start_time=datetime.now())
        self.handshakes.clear()
        
        logger.info(f"Starting packet capture on {self.adapter.interface}")
        logger.info(f"Capture file: {self.capture_file}")
        
        def packet_handler(pkt):
            """Handle captured packet."""
            if not self.is_capturing:
                return False  # Stop capture
            
            try:
                captured_pkt = self._parse_packet(pkt)
                if captured_pkt:
                    # Apply BSSID filter
                    if filter_bssid and captured_pkt.bssid != filter_bssid:
                        return
                    
                    self.packets.append(captured_pkt)
                    self._update_stats(pkt, captured_pkt)
                    
                    # Check for handshake packets
                    if capture_handshakes and EAPOL in pkt:
                        self._process_handshake(pkt, captured_pkt)
                    
                    # Call callback
                    if callback:
                        callback(captured_pkt)
                    
                    # Check packet count limit
                    if packet_count and len(self.packets) >= packet_count:
                        return False  # Stop capture
            
            except Exception as e:
                logger.error(f"Error processing packet: {e}")
        
        try:
            # Start sniffing
            packets = sniff(
                iface=self.adapter.interface,
                prn=packet_handler,
                timeout=duration,
                store=True
            )
            
            # Save to file
            if packets:
                wrpcap(str(self.capture_file), packets)
                logger.info(f"Saved {len(packets)} packets to {self.capture_file}")
        
        except Exception as e:
            logger.error(f"Capture error: {e}")
            raise CaptureError(f"Failed to capture packets: {e}")
        
        finally:
            self.is_capturing = False
            self.stats.end_time = datetime.now()
            if self.stats.start_time:
                self.stats.capture_duration = (
                    self.stats.end_time - self.stats.start_time
                ).total_seconds()
        
        return self.capture_file
    
    def stop_capture(self) -> None:
        """Stop packet capture."""
        if self.is_capturing:
            logger.info("Stopping packet capture")
            self.is_capturing = False
    
    def _parse_packet(self, pkt) -> Optional[CapturedPacket]:
        """Parse packet and extract information."""
        if not pkt.haslayer(Dot11):
            return None
        
        dot11 = pkt[Dot11]
        
        # Determine packet type
        packet_type = "unknown"
        if pkt.haslayer(Dot11Beacon):
            packet_type = "beacon"
        elif pkt.haslayer(Dot11ProbeReq):
            packet_type = "probe_request"
        elif pkt.haslayer(Dot11ProbeResp):
            packet_type = "probe_response"
        elif pkt.haslayer(Dot11Auth):
            packet_type = "authentication"
        elif pkt.haslayer(Dot11Deauth):
            packet_type = "deauthentication"
        elif pkt.haslayer(Dot11Disas):
            packet_type = "disassociation"
        elif pkt.haslayer(Dot11AssoReq):
            packet_type = "association_request"
        elif pkt.haslayer(Dot11AssoResp):
            packet_type = "association_response"
        elif pkt.haslayer(EAPOL):
            packet_type = "eapol"
        elif dot11.type == 2:
            packet_type = "data"
        
        # Extract MAC addresses
        source_mac = dot11.addr2
        dest_mac = dot11.addr1
        bssid = dot11.addr3
        
        # Extract SSID
        ssid = None
        if pkt.haslayer(Dot11Beacon) or pkt.haslayer(Dot11ProbeResp):
            try:
                ssid = pkt[Dot11Elt].info.decode('utf-8', errors='ignore')
            except:
                pass
        
        # Extract signal strength
        signal_strength = None
        if pkt.haslayer(RadioTap):
            try:
                signal_strength = pkt[RadioTap].dBm_AntSignal
            except:
                pass
        
        return CapturedPacket(
            timestamp=datetime.now(),
            packet_type=packet_type,
            source_mac=source_mac,
            dest_mac=dest_mac,
            bssid=bssid,
            ssid=ssid,
            channel=None,  # Would need to extract from RadioTap
            signal_strength=signal_strength,
            packet_size=len(pkt),
            raw_data=bytes(pkt) if len(bytes(pkt)) < 1024 else None
        )
    
    def _update_stats(self, pkt, captured_pkt: CapturedPacket) -> None:
        """Update capture statistics."""
        self.stats.total_packets += 1
        self.stats.data_bytes += captured_pkt.packet_size
        
        # Update frame type counters
        if captured_pkt.packet_type == "beacon":
            self.stats.beacon_frames += 1
        elif captured_pkt.packet_type == "probe_request":
            self.stats.probe_requests += 1
        elif captured_pkt.packet_type == "probe_response":
            self.stats.probe_responses += 1
        elif captured_pkt.packet_type == "authentication":
            self.stats.auth_frames += 1
        elif captured_pkt.packet_type == "deauthentication":
            self.stats.deauth_frames += 1
        elif captured_pkt.packet_type == "disassociation":
            self.stats.disassoc_frames += 1
        elif captured_pkt.packet_type == "data":
            self.stats.data_frames += 1
        elif captured_pkt.packet_type == "eapol":
            self.stats.eapol_frames += 1
    
    def _process_handshake(self, pkt, captured_pkt: CapturedPacket) -> None:
        """Process potential handshake packet."""
        if captured_pkt.bssid:
            self.handshakes[captured_pkt.bssid].append(pkt)
            logger.debug(f"EAPOL packet captured for {captured_pkt.bssid}")
    
    def get_stats(self) -> PacketStats:
        """Get capture statistics."""
        return self.stats
    
    def get_packets(self, filter_type: Optional[str] = None) -> List[CapturedPacket]:
        """
        Get captured packets.
        
        Args:
            filter_type: Filter by packet type
        
        Returns:
            List of captured packets
        """
        if filter_type:
            return [p for p in self.packets if p.packet_type == filter_type]
        return self.packets
    
    def get_handshakes(self) -> Dict[str, int]:
        """Get captured handshakes count by BSSID."""
        return {bssid: len(pkts) for bssid, pkts in self.handshakes.items()}
    
    def export_handshake(self, bssid: str, output_file: Optional[Path] = None) -> Optional[Path]:
        """
        Export captured handshake for a specific BSSID.
        
        Args:
            bssid: BSSID to export handshake for
            output_file: Output file path
        
        Returns:
            Path to exported file or None
        """
        if bssid not in self.handshakes or not self.handshakes[bssid]:
            logger.warning(f"No handshake captured for {bssid}")
            return None
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"handshake_{bssid.replace(':', '')}_{timestamp}.pcap"
        
        try:
            wrpcap(str(output_file), self.handshakes[bssid])
            logger.info(f"Exported handshake to {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Failed to export handshake: {e}")
            return None

