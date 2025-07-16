import subprocess
import re
import os

def check_ftp_package():
    try:
        command = subprocess.run("sudo yum list installed | grep ftpd", shell=True, capture_output=True, text=True)
        if command.returncode == 0:
            return ("Fail", f"ftpd package was found: {command.stdout}")
        else:
            return ("Pass", "No ftpd package was found was found")
    except Exception as e:
        return f"Error: {e}"

print(check_ftp_package())
