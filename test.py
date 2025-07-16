import subprocess
import re
import os

def check_audit_services():
    try:
        command = subprocess.run("systemctl status auditd.service", shell=True, capture_output=True, text=True)
        output = command.stdout.strip()
        for line in output.splitlines():
            if line.lstrip().startswith("Active:"):
                    if "active (running)" in line.lower():
                        return ("Pass", "Audit service is currently running")
                    else:
                        return ("Fail", "Audit service is not currently running")
    except Exception as e:
        return f"Error: {e}"

print(check_audit_services())
