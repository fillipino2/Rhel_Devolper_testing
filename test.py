import subprocess
import re
import os
import glob

def check_audit_shadow_file():
    try:

        command = subprocess.run("grep /etc/shadow /etc/audit/audit.rules",
                                 shell=True,
                                 capture_output=True,
                                 text=True)
        
        output = command.stdout.strip()
        for line in output.splitlines():
            if "-w /etc/shadow" in line:
                match = re.search(r"-p\s*([rwa]+)", line)
                if match:
                    perms = match.group(1)
                    if "w" in perms and "a" in perms:
                        return ("Pass", f"Audit file is correct: {output}")
        return ("Fail", f"What could this be: {output}")

    except Exception as e:
        return f"Error: {e}"
print(check_audit_shadow_file())
