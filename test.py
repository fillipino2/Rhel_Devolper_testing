import subprocess
import re
import os
import glob

def check_audit_shadow_file():
    try:
        command = subprocess.run(
            "grep /etc/shadow /etc/audit/audit.rules",
            shell=True,
            capture_output=True,
            text=True
        )

        output = command.stdout.strip()

        if command.returncode != 0:
            return ("Fail", f"No entries found for /etc/shadow in audit.rules. Error: {command.stderr.strip()}")

        for line in output.splitlines():
            if "-w /etc/shadow" in line:
                match = re.search(r"-p\s*([rwa]+)", line)
                if match:
                    perms = match.group(1)
                    if "w" in perms and "a" in perms:
                        return ("Pass", f"Audit rule for /etc/shadow includes write and append: {line}")
                    else:
                        return ("Fail", f"Permissions missing 'w' or 'a': {line}")
                else:
                    return ("Fail", f"No -p permissions found in line: {line}")

        return ("Fail", f"No valid audit rules found for /etc/shadow: {output}")

    except Exception as e:
        return ("Error", str(e))
print(check_audit_shadow_file())
