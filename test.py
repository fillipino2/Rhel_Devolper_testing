import subprocess
import re
import os
import glob

def check_pki_status():
    
    try:

        command = subprocess.run("grep certificate_verification /etc/sssd/sssd.conf /etc/sssd/conf.d/*.conf | grep -v \"^#\"",
                                 shell=True,
                                 capture_output=True,
                                 text=True,)
        if command.returncode == 0:
            output = command.stdout.strip()
            if "=" in output:
                key, val = [x.strip() for x in output.split("=", 1)]
                if key == "certificate_verification" and val == "ocsp_dgst=sha1":
                    return ("Pass", f"Im not sure what to write: {output}")
                else:
                    return ("Fail", f"Im not sure what to write: {output}")
        else:
            return ("Fail", f"but why {output}")
    except Exception as e:
        return f"Error: {e}"
print(check_pki_status())
