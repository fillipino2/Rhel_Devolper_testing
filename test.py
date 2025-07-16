import subprocess
import re
import os

def check_permitemptypassword_sshd():
    try:
        with open("/etc/ssh/sshd_config", "r") as permitpasswd:
            for line in permitpasswd:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue
                
                if line.lower().startswith("permitemptypassword"):
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].lower() == "no":
                        return ("PermitEmptyPasswords", "pass", "set to no")
                    else:
                        return ("PermitEmptyPasswords", "Fail", f"{parts[1] if len(parts) > 1 else 'missing'}")
        return (" PermitEmptyPasswords", "Pass", "Directive not found")
    except Exception as e:
        return ("PermitEmptyPasswords", "error", str(e))

print(check_permitemptypassword_sshd())
