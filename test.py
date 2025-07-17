import subprocess
import re
import os
import glob

def check_pki_status():
    try:
        command = subprocess.run(
            "grep certificate_verification /etc/sssd/sssd.conf /etc/sssd/conf.d/*.conf | grep -v \"^#\"",
            shell=True,
            capture_output=True,
            text=True,
        )

        output = command.stdout.strip()

        if command.returncode == 0:
            if "=" in output:
                key, val = [x.strip() for x in output.split("=", 1)]
                if key == "certificate_verification" and val == "ocsp_dgst=sha1":
                    return ("Pass", f"certificate_verification is correctly set: {output}")
                else:
                    return ("Fail", f"certificate_verification is incorrectly set: {output}")
            else:
                return ("Fail", f"No key=value pair found in output: {output}")
        else:
            return ("Fail", f"No matching configuration found. Output: {output or command.stderr.strip()}")

    except Exception as e:
        return ("Error", str(e))
print(check_pki_status())
