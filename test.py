import subprocess
import re
import os
import glob


def check_ctrlaltdelete_burst():
    try:
        with open("/etc/systemd/system.conf", "r") as output:
            for line in output:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue  # skip empty or commented lines

                if "CtrlAltDelBurstAction" in line and "=" in line:
                    key, val = [x.strip() for x in line.split("=", 1)]
                    if key == "CtrlAltDelBurstAction":
                        if val == "none":
                            return ("Pass", f"CtrlAltDelBurstAction is correctly set to 'none' in /etc/systemd/system.conf: {line}")
                        else:
                            return ("Fail", f"CtrlAltDelBurstAction is set to '{val}' instead of 'none' in /etc/systemd/system.conf: {line}")

        return ("Fail", "CtrlAltDelBurstAction setting not found in /etc/systemd/system.conf")

    except Exception as e:
        return ("Error", str(e))
                
print(check_ctrlaltdelete_burst())
