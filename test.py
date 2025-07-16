import subprocess
import re
import os

def check_shosts_file():
    try:
        command = subprocess.run("find / -name '*.shosts' 2>/dev/null", shell=True, capture_output=True, text=True)
        output = command.stdout.strip()
        if output:
            return "Fail"
        else:
            return "Pass"
    except Exception as e:
        return f"Error: {e}"

print(check_shosts_file())
