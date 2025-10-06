# WIFIjam Installation Guide

Complete installation instructions for all supported platforms.

## Table of Contents
- [Linux Installation](#linux-installation)
- [macOS Installation](#macos-installation)
- [Windows Installation](#windows-installation)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Linux Installation

### Debian/Ubuntu/Mint

```bash
# 1. Update system
sudo apt-get update
sudo apt-get upgrade -y

# 2. Install system dependencies
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    aircrack-ng \
    iw \
    wireless-tools \
    net-tools \
    git

# 3. Install WIFIjam
git clone https://github.com/AryanVBW/WIFIjam.git
cd WIFIjam
pip3 install -e .

# 4. Verify installation
wifijam --version
```

### Arch/Manjaro

```bash
# 1. Update system
sudo pacman -Syu

# 2. Install system dependencies
sudo pacman -S \
    python \
    python-pip \
    aircrack-ng \
    iw \
    wireless_tools \
    net-tools \
    git

# 3. Install WIFIjam
git clone https://github.com/AryanVBW/WIFIjam.git
cd WIFIjam
pip install -e .

# 4. Verify installation
wifijam --version
```

### Fedora/RHEL/CentOS

```bash
# 1. Update system
sudo dnf update -y

# 2. Install system dependencies
sudo dnf install -y \
    python3 \
    python3-pip \
    python3-devel \
    aircrack-ng \
    iw \
    wireless-tools \
    net-tools \
    git

# 3. Install WIFIjam
git clone https://github.com/AryanVBW/WIFIjam.git
cd WIFIjam
pip3 install -e .

# 4. Verify installation
wifijam --version
```

## macOS Installation

**Note**: macOS has limited support. Monitor mode and attacks are not supported on most hardware.

```bash
# 1. Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install Python 3
brew install python3

# 3. Install WIFIjam
git clone https://github.com/AryanVBW/WIFIjam.git
cd WIFIjam
pip3 install -e .

# 4. Verify installation
wifijam --version
```

### macOS Limitations
- Monitor mode: Not supported (except with specific USB adapters)
- Packet injection: Not supported
- Attacks: Not available
- Scanning: Limited functionality

## Windows Installation

**Note**: Windows has very limited support. Full functionality requires WSL2.

### Option 1: WSL2 (Recommended)

```powershell
# 1. Install WSL2
wsl --install

# 2. Restart computer

# 3. Open Ubuntu from Start Menu

# 4. Follow Linux (Ubuntu) installation instructions
```

### Option 2: Native Windows (Limited)

```powershell
# 1. Install Python 3.8+
# Download from: https://www.python.org/downloads/

# 2. Install Git
# Download from: https://git-scm.com/download/win

# 3. Open PowerShell as Administrator

# 4. Install WIFIjam
git clone https://github.com/AryanVBW/WIFIjam.git
cd WIFIjam
pip install -e .

# 5. Verify installation
wifijam --version
```

### Windows Limitations
- Monitor mode: Not supported
- Packet injection: Not supported
- Attacks: Not available
- Scanning: Basic network information only

## Verification

After installation, verify everything is working:

```bash
# Check version
wifijam --version

# Check system information
sudo wifijam info

# List WiFi adapters
sudo wifijam adapters

# Start GUI (will open browser)
sudo wifijam gui
```

## Troubleshooting

### Python Version Issues

```bash
# Check Python version (must be 3.8+)
python3 --version

# If version is too old, install newer Python
# Ubuntu/Debian
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.11

# Use specific Python version
python3.11 -m pip install -e .
```

### Permission Errors

```bash
# Install for user only (no sudo)
pip3 install --user -e .

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Missing Dependencies

```bash
# Linux: Install all at once
sudo apt-get install -y aircrack-ng iw wireless-tools net-tools

# Verify installation
which airmon-ng airodump-ng aireplay-ng iw
```

### Aircrack-ng Not Found

```bash
# Ubuntu/Debian
sudo apt-get install aircrack-ng

# Arch
sudo pacman -S aircrack-ng

# Fedora
sudo dnf install aircrack-ng

# Verify
airmon-ng --help
```

### Import Errors

```bash
# Reinstall dependencies
pip3 install --upgrade -r requirements.txt

# Or install individually
pip3 install aiohttp aiohttp-cors scapy
```

### WiFi Adapter Not Detected

```bash
# Check if adapter is recognized by system
lsusb  # For USB adapters
lspci  # For PCI adapters
iw dev  # List wireless interfaces

# Check if driver is loaded
lsmod | grep -i wifi
lsmod | grep -i 80211

# Restart network manager
sudo systemctl restart NetworkManager
```

### Monitor Mode Not Working

```bash
# Check adapter capabilities
iw list | grep -A 10 "Supported interface modes"

# Kill conflicting processes
sudo airmon-ng check kill

# Try manual monitor mode
sudo ip link set wlan0 down
sudo iw wlan0 set monitor control
sudo ip link set wlan0 up

# Verify
iw wlan0 info
```

### Port Already in Use

```bash
# Check what's using port 8080
sudo lsof -i :8080

# Kill the process
sudo kill -9 <PID>

# Or use different port
wifijam config --set server.port=8888
```

### Firewall Issues

```bash
# Ubuntu/Debian
sudo ufw allow 8080/tcp

# Fedora/RHEL
sudo firewall-cmd --add-port=8080/tcp --permanent
sudo firewall-cmd --reload
```

## Uninstallation

```bash
# Remove WIFIjam
pip3 uninstall wifijam

# Remove configuration (optional)
rm -rf ~/.wifijam

# Remove system dependencies (optional)
# Ubuntu/Debian
sudo apt-get remove aircrack-ng iw wireless-tools
```

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [main README](README_NEW.md)
3. Search [existing issues](https://github.com/AryanVBW/WIFIjam/issues)
4. Create a [new issue](https://github.com/AryanVBW/WIFIjam/issues/new) with:
   - Your OS and version
   - Python version
   - Complete error message
   - Steps to reproduce

## Next Steps

After successful installation:

1. Read the [Quick Start Guide](README_NEW.md#-quick-start-guide)
2. Check [Usage Documentation](README_NEW.md#-usage)
3. Review [API Documentation](README_NEW.md#-api-documentation)
4. Understand [Legal Considerations](README_NEW.md#-security--legal)

---

**Remember**: Always use WIFIjam responsibly and legally!

