import subprocess
import re

def check_selinux_target_policy():
    try:
        command = subprocess.run(["sestatus"], capture_output=True,text=True)
        output = command.stdout.lower()
        for line in output.splitlines():
            if line.startswith("loaded policy name:"):
                status = line.split(":", 1)[1].strip()
                if status == "targeted":
                    return ("Pass", "SELinux is enforcing targeted policies")
                else:
                    return ("Fail", f"SELinux is {status}")
        return ("Fail", "SELinux loaded policy name was not found")
    except Exception as e:
        return ("Error", str(e))

print(check_selinux_target_policy())
