import subprocess
import re

def check_selinux_target_policy():
    try:
        verify = subprocess.run("grep -i selinuxtype /etc/selinux/config | grep -v '^#'",
                                shell=True,
                                capture_output=True,
                                text=True)
        if verify.returncode != 0 or not verify.stdout.strip():
            return "Fail"
        verification = verify.stdout.lower().strip()
        final = verification.split("=", 1)[1].strip()
        result = subprocess.run(["sestatus"], capture_output=True, text=True)
        output = result.stdout.lower()
        for line in output.splitlines():
            if line.startswith("Loaded policy name:"):
                target = line.split(":", 1)[1].strip()
                if target == "targeted" and final == "targeted":
                    return "Pass"
                else:
                    return "Fail"
        return "Fail"
    except Exception as e:
        return f"Error: {e}"

print(check_selinux_target_policy())
