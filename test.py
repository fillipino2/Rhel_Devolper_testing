import subprocess
import re

def check_selinux_enabled():
    try:
        result = subprocess.run(["sestatus"], capture_output=True,text=True )
        output = result.stdout.lower()
        for line in output.splitlines():
            if line.startswith("SELinux status:"):
                status = line.split(":", 1)[1].strip()
                if status == "enabled":
                    return "Pass"
                else:
                    return "Fail"
        return "Fail"
    except Exception as e:
        return f"Error: {e}"
