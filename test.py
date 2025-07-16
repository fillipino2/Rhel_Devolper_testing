import subprocess
import re
import os
import glob

def check_promisc_mode():
    try:
        command = subprocess.run("sudo ip link | grep -i promisc", shell=True, capture_output=True, text=True)
        output = command.stdout.strip()
        if output:
            return ("Fail", f"promisc mode is enabled and needs to be turned off: {output}")
        else:
            return ("Pass", "promisc mode is disabled")
    except Exception as e:
        return f"Error: {e}"
print(check_promisc_mode())
