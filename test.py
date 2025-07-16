import subprocess
import re

def check_signed_pacakges_dnf():
    try:
        with open("/etc/dnf/dnf.conf", "r") as dnf:
            for line in dnf:
                line = line.strip()
                if  line.startswith("localpkgcheck_gpg"):
                    key_value = [s.strip() for s in line.split("=", 1)]
                    if len(key_value) == 2 and key_value[1].lower() == "true":
                        return "Pass"
                else:
                    return "Fail"
    except Exception as e:
        return f"Error; {e}"
