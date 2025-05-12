@echo off
REM Advanced WiFi Info Script for Windows
REM Features: list adapters, info, warnings, run info script

REM List all WiFi adapters
wmic nic where (NetEnabled=true and AdapterTypeID=9) get Name,DeviceID

REM Warn about monitor mode/packet injection
echo.
echo [!] WARNING: Windows does NOT support monitor mode or packet injection for most adapters.
echo     WiFi jamming/deauth attacks are NOT possible on Windows.
echo     You can only view WiFi info.
echo.

set /p runpy=Do you want to run the WiFi info script (windows10-wifi.py)? [Y/N]: 
if /I "%runpy%"=="Y" (
    if exist red-python-scripts\windows10-wifi.py (
        python red-python-scripts\windows10-wifi.py
    ) else (
        echo [!] Script not found: red-python-scripts\windows10-wifi.py
    )
) else (
    echo Exiting.
) 