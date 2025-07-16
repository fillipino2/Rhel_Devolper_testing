import subprocess
import re
import os
import glob

def check_postfix():
    try:
        command = subprocess.run("yum list installed postfix",
                                 shell=True,
                                 capture_output=True,
                                 text=True)
        if command.returncode != 0:
            return ("N/A", "Since postifix is not installed this is N/A")
        
        config_check = subprocess.run("postconf -n smtpd_client_restrictions",
                                      shell=True,
                                      capture_output=True,
                                      text=True)
        if config_check.returncode != 0:
            return "Not Applicable"
        
        output = config_check.stdout.strip()

        if "smtpd_client_restrictions" in output and "=" in output:
            key, val = [x.strip() for x in output.split("=",1)]
            if key == "smtpd_client_restrictions" and val == "permit_mynetworks, reject":
                return "Pass"
            else:
                return "Fail"
    except Exception as e:
        return f"Error {e}"
print(check_postfix())
