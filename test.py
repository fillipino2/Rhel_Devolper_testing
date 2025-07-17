import subprocess
import re
import os
import glob


def check_ctrlaltdelete_burst():
    try:
        with open("/etc/systemd/system.conf", "r") as output:
            for line in output:
                line = line.strip()
                if "CtrlAltDelBurstAction" in line and "=" in line:
                    key, val = [x.strip() for x in line.split("=, 1")]
                    if key == "CtrlAltDelBurstAction" and val == "none":
                        return "Pass"
                    else:
                        return "Fail"
            return "Fail"
    except Exception as e:
        return f"Error: {e}"
                
print(check_ctrlaltdelete_burst())
