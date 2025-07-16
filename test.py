import subprocess
import re

def check_signed_packages_dnf():
    try:
        with open("/etc/dnf/dnf.conf", "r") as dnf:
            for line in dnf:
                line = line.strip()
                if line.startswith("localpkgcheck_gpg"):
                    key_value = [s.strip() for s in line.split("=", 1)]
                    if len(key_value) == 2 and key_value[1].lower() == "true":
                        return ("Pass", "'localpkgcheck_gpg=true' is set correctly")
                    else:
                        return ("Fail", f"Found 'localpkgcheck_gpg={key_value[1]}', expected 'true'")
        # If the loop finishes and no match was found
        return ("Fail", "'localpkgcheck_gpg=true' is missing from /etc/dnf/dnf.conf")

    except Exception as e:
        return ("Error", str(e))

