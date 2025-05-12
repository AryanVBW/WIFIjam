# WIFIjam Universal WiFi Deauthenticator & Info Tool
<p align="center">
<img src="https://raw.githubusercontent.com/AryanVBW/WIFIjam/main/Logo/OIG__17_-removebg-preview.png" height="250"><br>
A WIFi Jamer  <img src="https://raw.githubusercontent.com/AryanVBW/WIFIjam/main/wifiB.png" height="20">, powered by Python <img src="https://raw.githubusercontent.com/AryanVBW/WIFIjam/main/python.png" height="12">
</p>

## Features
- Cross-platform: Works on Linux, macOS, and Windows
- Detects OS and WiFi adapter capabilities
- Lists WiFi adapters and scans for networks (all OSes)
- On Linux, can attempt deauth (with monitor mode and compatible adapter)
- On macOS/Windows, shows detailed WiFi info and warns about limitations
- Robust error handling, clear user guidance, and optional scan result saving

## Requirements
- Python 3.x
- [Scapy](https://scapy.net/) (auto-installs if missing)
- Linux: `iw`, `iwconfig`, `iwlist` or `iw dev`, `ip`, `sudo`
- macOS: `airport` utility (included on most systems)
- Windows: No extra requirements (uses built-in `netsh`)

## Usage

### Linux
1. (Optional) Put your WiFi adapter in monitor mode (the script can attempt this for you):
   ```bash
   sudo iw <iface> set monitor control
   sudo ip link set <iface> up
   ```
2. Run the script as root:
   ```bash
   sudo python3 wifi_deauth_universal.py
   ```
3. Follow the prompts to select your interface, scan for networks, and (if supported) perform a deauth attack.

### macOS
1. Run the script:
   ```bash
   python3 wifi_deauth_universal.py
   ```
2. You can scan for nearby WiFi networks and view info. Deauth/jamming is not supported on most hardware.

### Windows
1. Run the script:
   ```cmd
   python wifi_deauth_universal.py
   ```
2. You can scan for nearby WiFi networks and view info. Deauth/jamming is not supported on most hardware.

## Capabilities & Limitations
- **Linux:**
  - Can perform deauth/jamming if you have a compatible adapter in monitor mode.
  - Can scan for networks and show info.
- **macOS:**
  - Can scan for networks and show info.
  - Deauth/jamming is not supported except with rare USB adapters and custom drivers.
- **Windows:**
  - Can scan for networks and show info.
  - Deauth/jamming is not supported except with rare hardware (e.g., AirPcap).

## Safety & Disclaimer
- **This tool is for educational and authorized security testing only.**
- Unauthorized use of WiFi jamming or deauthentication is illegal in many countries.
- The authors provide no warranty and are not responsible for misuse or damages.

## Credits
- Inspired by the open-source community and [Scapy](https://scapy.net/).
- Thanks to all contributors and testers.



## <img src="https://raw.githubusercontent.com/AryanVBW/WIFIjam/main/wifiB.png" height="40">Features
- JAM 2.4Hz wifi or Mobile hostpost
- Jam 5Hz wifi or Mobile hostpost 
- deauthentication attack 

## Prerequisites 
 - Monitor mode and Packet injection supported wifi adapter
 - Install python3
    - Debian, Ubuntu, Etc
        - `sudo apt-get install python3`
    - Fedora, Oracle, Red Hat, etc
        -  `su -c "yum install python"`
    - Windows 
        -Coming soon
## <img src="https://raw.githubusercontent.com/AryanVBW/WIFIjam/main/wifiB.png" height="40">Installation
```bash 
 git clone https://github.com/AryanVBW/WIFIjam.git
 cd WIFIjam
 python3 wifi1.py 
```
   or
   `python3 wifi2.py`

   <p align="center"> 
  Visitor count<br>
  <img src="https://profile-counter.glitch.me/Aryanvbw/count.svg" />

## Thank You 🙏

This project was inspired by the incredible YouTube tutorial "WIFI Jamming in Python" and [Python Network Hacking with Kali Linux and Scapy](https://youtu.be/O1jpck31Ask?si=4h8BinIB1dnRQrQs),  which provided valuable insights into building an Exif data tool.

A heartfelt thanks to David Bombal for his fantastic [red python script on GitHub](https://github.com/davidbombal/red-python-scripts), which served as a guiding resource during development.

To the open-source community, developers, and testers: your support makes this project thrive.
## Disclaimer
<b>Aryan Provides no warranty with this software and will not be responsible for any direct or indirect damage caused due to the usage of this tool.<br>
Wifi Jam is built for both Educational and Internal use ONLY.</b>

<br>
<p align="center">Made with ❤️ By <a href="aryanvbw.github.io">*Vivek W*</a></p>
<p align="center" style="font-size: 8px">v1.1.2</p>

