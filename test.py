import subprocess
import re
import os

def check_auto_login_with_gui():
    path = "/etc/gdm/custom.conf"
    if not os.path.exists(path):
        return ("N/A", "custom.conf is not present; GUI is most likely not in use, Ask stakeholder to confirm")
    
    try:

        with open("/etc/gdm/custom.conf", "r") as auto:
            if 
            for line in auto:
                line = line.strip().lower()
                if line.startswith("automaticloginenable"):
                    if "#" in line or ";" in line:
                        continue
                    value = line.split("=", 1)[1].strip()
                    return "Pass" if value == "false" else "fail"
        return "Fail"
    except Exception as e:
        return f"Error: {e}"

print(check_auto_login_with_gui())
