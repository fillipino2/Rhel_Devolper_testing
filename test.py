import subprocess
import re
import os

def check_os_release(min_required_version="8.10"):
    try:
        command = subprocess.run("sudo cat /etc/redhat-release", shell=True, capture_output=True, text=True)
        result = command.stdout.strip()
        match = re.search(r'release\s+(\d+\.\d+)', result.lower())
        if not match:
            return "Fail"
        current_version = float(match.group(1))
        required_version = float(min_required_version)
        if current_version >= required_version:
            return "Pass"
        else:
            return "Fail"
        
    except Exception as e:
        return f"Error: {e}"

print(check_os_release())
