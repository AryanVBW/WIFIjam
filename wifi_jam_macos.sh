#!/bin/bash
# Advanced WiFi Manager for macOS
# Features: auto-detect adapters, scan, info, warnings, graceful fallback

set -e

# Check for airport utility
AIRPORT_PATH="/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
if [ ! -x "$AIRPORT_PATH" ]; then
    echo "[!] 'airport' utility not found. macOS WiFi scanning may not work."
    exit 1
fi

# List all network interfaces
adapters=($(networksetup -listallhardwareports | awk '/Device/ {print $2}'))
if [ ${#adapters[@]} -eq 0 ]; then
    echo "[!] No network adapters found."
    exit 1
fi

echo "Available network adapters:"
for i in "${!adapters[@]}"; do
    echo "$i) ${adapters[$i]}"
done

read -p "Select adapter number: " idx
adapter="${adapters[$idx]}"

# Check if adapter is WiFi
if ! networksetup -listallhardwareports | grep -A 1 "$adapter" | grep -q Wi-Fi; then
    echo "[!] Selected adapter may not be a WiFi adapter."
fi

# Warn about monitor mode/packet injection
cat <<EOF
[!] Note: macOS does NOT natively support monitor mode or packet injection.
    - You can scan for networks, but cannot perform jamming/deauth attacks.
    - For advanced features, use a compatible USB WiFi adapter with custom drivers (rare).
EOF

# Scan for WiFi networks
sudo "$AIRPORT_PATH" scan

echo "[+] Scan complete. If you need jamming/monitor mode, use Linux." 