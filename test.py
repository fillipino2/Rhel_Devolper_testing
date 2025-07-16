import subprocess
import re

def check_selinux_enabled():
    try:
        result = subprocess.run(["sestatus"], capture_output=True, text=True)
        output = result.stdout.lower()

        for line in output.splitlines():
            if line.startswith("selinux status:"):
                status = line.split(":", 1)[1].strip()
                if status == "enabled":
                    return ("Pass", "SELinux is enabled")
                else:
                    return ("Fail", f"SELinux is {status}")
        return ("Fail", "SELinux status line not found in sestatus output")

    except Exception as e:
        return ("Error", str(e))
print(check_selinux_enabled())
