# WIFIjam v2.0 - Professional WiFi Security Testing Tool

<p align="center">
<img src="https://raw.githubusercontent.com/AryanVBW/WIFIjam/main/Logo/OIG__17_-removebg-preview.png" height="250"><br>
A Professional WiFi Security Testing Tool with Modern GUI
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
  <img src="https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg" alt="Platform">
</p>

## 🚀 What's New in v2.0

- **🎨 Modern Web-Based GUI** - Beautiful, responsive dashboard with real-time updates
- **🔌 REST API & WebSocket** - Full-featured API for programmatic access
- **📦 Pip Installable** - Install with a single command: `pip install wifijam`
- **🖥️ Cross-Platform** - Works on Linux, macOS, and Windows
- **⚡ Real-Time Monitoring** - Live network discovery and attack progress
- **🛠️ Professional Architecture** - Clean, modular, production-ready code
- **📊 Advanced Features** - Monitor mode management, multi-adapter support
- **🔒 Security Focused** - Proper error handling and permission management

## ✨ Features

### Core Capabilities
- **WiFi Network Scanning** - Discover nearby networks with detailed information
- **Monitor Mode Management** - Enable/disable monitor mode on compatible adapters
- **Deauthentication Attacks** - Disconnect devices from target networks
- **2.4GHz & 5GHz Jamming** - Disrupt WiFi communications on both bands
- **Multi-Adapter Support** - Detect and manage multiple WiFi adapters
- **Real-Time Updates** - WebSocket-based live data streaming

### User Interface
- **Web Dashboard** - Modern, intuitive web interface
- **Network Visualization** - Interactive network discovery table
- **Attack Control Panel** - Easy-to-use attack configuration
- **System Monitoring** - Real-time system and adapter status
- **Configuration Management** - Persistent settings and preferences
- **Comprehensive Logging** - Detailed logs with filtering and export

### Technical Features
- **Cross-Platform** - Linux (primary), macOS (limited), Windows (info only)
- **Multiple Attack Methods** - aireplay-ng, Scapy, custom implementations
- **Async Architecture** - Non-blocking operations with asyncio
- **RESTful API** - Complete API for automation and integration
- **WebSocket Support** - Real-time bidirectional communication
- **Modular Design** - Clean separation of concerns

## 📋 Requirements

### System Requirements
- **Python 3.8+**
- **Root/Administrator privileges** (for monitor mode and attacks)
- **WiFi adapter with monitor mode support** (for attacks)

### Linux (Recommended)
```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y aircrack-ng iw wireless-tools net-tools

# Arch/Manjaro
sudo pacman -S aircrack-ng iw wireless_tools net-tools

# Fedora/RHEL
sudo dnf install aircrack-ng iw wireless-tools net-tools
```

### macOS
```bash
# Limited support - scanning only
# Monitor mode and attacks not supported on most hardware
brew install python3
```

### Windows
```bash
# Very limited support - network information only
# Requires WSL2 for full functionality
# Install WSL2 and follow Linux instructions
```

## 🔧 Installation

### Method 1: Pip Install (Recommended)
```bash
# Install from PyPI (when published)
pip install wifijam

# Or install from source
git clone https://github.com/AryanVBW/WIFIjam.git
cd WIFIjam
pip install -e .
```

### Method 2: Manual Installation
```bash
# Clone repository
git clone https://github.com/AryanVBW/WIFIjam.git
cd WIFIjam

# Install dependencies
pip install -r requirements.txt

# Run directly
python -m wifijam.cli gui
```

## 🎯 Usage

### GUI Mode (Default)
```bash
# Start with GUI (opens browser automatically)
sudo wifijam gui

# Start without opening browser
sudo wifijam gui --no-browser

# Then navigate to: http://localhost:8080
```

### Command Line Interface
```bash
# Display system information
wifijam info

# List WiFi adapters
wifijam adapters

# Show configuration
wifijam config --show

# Set configuration
wifijam config --set server.port=8888

# Reset configuration
wifijam config --reset
```

### Python API
```python
from wifijam.api.server import APIServer
from wifijam.core.config import Config

# Create and configure server
config = Config()
config.server.port = 8080

# Start server
server = APIServer(config)
server.run()
```

## 📖 Quick Start Guide

### 1. Check System Compatibility
```bash
sudo wifijam info
```
This will show your system information, capabilities, and dependencies.

### 2. List WiFi Adapters
```bash
sudo wifijam adapters
```
Verify your WiFi adapter is detected and supports monitor mode.

### 3. Start the GUI
```bash
sudo wifijam gui
```
The dashboard will open in your default browser.

### 4. Using the Dashboard

1. **Select Adapter** - Choose your WiFi adapter from the configuration
2. **Enable Monitor Mode** - Toggle monitor mode (Linux only)
3. **Scan Networks** - Start scanning to discover nearby networks
4. **Select Target** - Click "Target" on a discovered network
5. **Configure Attack** - Choose attack type and parameters
6. **Execute** - Start the attack and monitor progress

## 🏗️ Architecture

```
wifijam/
├── core/               # Core functionality
│   ├── config.py      # Configuration management
│   ├── logger.py      # Logging system
│   ├── system.py      # System detection
│   └── exceptions.py  # Custom exceptions
├── wifi/              # WiFi operations
│   ├── adapter.py     # Adapter management
│   ├── scanner.py     # Network scanning
│   ├── monitor.py     # Monitor mode
│   └── attack.py      # Attack operations
├── api/               # API server
│   ├── server.py      # Main server
│   ├── websocket.py   # WebSocket manager
│   └── routes.py      # API routes
└── cli.py             # Command-line interface
```

## 🔌 API Documentation

### REST API Endpoints

#### System
- `GET /api/system/info` - Get system information
- `GET /api/system/dependencies` - Check dependencies

#### Adapters
- `GET /api/adapters` - List all adapters
- `GET /api/adapters/{interface}` - Get adapter details
- `POST /api/adapters/{interface}/select` - Select adapter

#### Monitor Mode
- `POST /api/monitor/enable` - Enable monitor mode
- `POST /api/monitor/disable` - Disable monitor mode
- `GET /api/monitor/status` - Get monitor status

#### Scanning
- `POST /api/scan/start` - Start network scan
- `POST /api/scan/stop` - Stop scan
- `GET /api/scan/networks` - Get discovered networks
- `GET /api/scan/status` - Get scan status

#### Attacks
- `POST /api/attack/start` - Start attack
- `POST /api/attack/stop` - Stop attack
- `GET /api/attack/status` - Get attack status

#### Configuration
- `GET /api/config` - Get configuration
- `POST /api/config` - Update configuration
- `POST /api/config/reset` - Reset configuration

### WebSocket Events

Connect to `ws://localhost:8080/ws`

**Server → Client Events:**
- `connected` - Connection established
- `network_discovered` - New network found
- `attack_progress` - Attack progress update
- `monitor_mode` - Monitor mode status change
- `system_event` - System event notification

**Client → Server Events:**
- `ping` - Heartbeat
- `subscribe` - Subscribe to events

## 🛡️ Security & Legal

### ⚠️ Important Disclaimer

**This tool is for educational and authorized security testing ONLY.**

- Only use on networks you own or have explicit written permission to test
- Unauthorized WiFi jamming/deauthentication is **ILLEGAL** in most countries
- The authors provide **NO WARRANTY** and are **NOT RESPONSIBLE** for misuse
- Users are solely responsible for compliance with local laws and regulations

### Legal Considerations

- **United States**: Violates FCC regulations (47 U.S.C. § 333)
- **European Union**: Violates Radio Equipment Directive
- **United Kingdom**: Violates Wireless Telegraphy Act 2006
- **Canada**: Violates Radiocommunication Act
- **Australia**: Violates Radiocommunications Act 1992

**Penalties can include:**
- Heavy fines (up to $100,000+ USD)
- Criminal prosecution
- Imprisonment
- Civil liability

### Ethical Use

✅ **Acceptable Use:**
- Testing your own networks
- Authorized penetration testing
- Educational research in controlled environments
- Security audits with written permission

❌ **Unacceptable Use:**
- Attacking public WiFi networks
- Disrupting others' internet access
- Unauthorized network testing
- Malicious intent

## 🐛 Troubleshooting

### Monitor Mode Issues
```bash
# Check if adapter supports monitor mode
iw list | grep -A 10 "Supported interface modes"

# Kill conflicting processes
sudo airmon-ng check kill

# Manually enable monitor mode
sudo ip link set wlan0 down
sudo iw wlan0 set monitor control
sudo ip link set wlan0 up
```

### Permission Errors
```bash
# Always run with sudo on Linux
sudo wifijam gui

# Check if running as root
id -u  # Should return 0
```

### No Networks Found
- Verify adapter is in monitor mode
- Check if adapter supports monitor mode
- Ensure there are networks in range
- Try increasing scan duration

### Dependencies Missing
```bash
# Install all dependencies
sudo apt-get install -y aircrack-ng iw wireless-tools

# Verify installation
which airmon-ng airodump-ng aireplay-ng
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👏 Credits & Acknowledgments

- Inspired by [WIFI Jamming in Python](https://youtu.be/XUncozRGbcs?si=me-KstWB0snLEfs4)
- David Bombal's [red python scripts](https://github.com/davidbombal/red-python-scripts)
- [Scapy](https://scapy.net/) - Packet manipulation library
- [Aircrack-ng](https://www.aircrack-ng.org/) - WiFi security tools
- The open-source community

## 📧 Contact

- **Author**: Vivek W (AryanVBW)
- **Email**: admin@aryanvbw.live
- **GitHub**: [@AryanVBW](https://github.com/AryanVBW)
- **Website**: [aryanvbw.github.io](https://aryanvbw.github.io)
- **Instagram**: [@Aryan_Technolog1es](https://instagram.com/Aryan_Technolog1es)

## 📊 Project Stats

<p align="center">
  <img src="https://profile-counter.glitch.me/Aryanvbw/count.svg" alt="Visitor count">
</p>

---

<p align="center">
Made with ❤️ by <a href="https://aryanvbw.github.io">Vivek W</a><br>
v2.0.0 © 2024
</p>

