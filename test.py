import subprocess
import re
import os

def check_ctl_alt_del():
    try:
        command = subprocess.run("sudo systemctl status ctrl-alt-del.target", shell=True, capture_output=True, text=True)
        result = command.stdout.strip().lower()
        for line in result.splitlines():
            if line.startswith("loaded:"):
                key_value = [s.strip() for s in line.split(":",1)]
                if len(key_value) == 2 and "masked" in key_value[1].lower():
                    return "Pass"
        return "Fail"
    except Exception as e:
        return f"Error: {e}"

print(check_ctl_alt_del())
