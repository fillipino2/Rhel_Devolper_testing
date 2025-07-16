import subprocess
import re

def check_auto_login_with_gui():
    try:
        with open("/etc/gdm/custom.conf", "r") as auto:
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
