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

        if command.returncode == 2:
            # Actual error (e.g., file not found)
            return ("Error", f"Grep error: {command.stderr.strip()}")

        if command.returncode == 1 or not output:
            # No match found
            return ("Fail", "No audit rule found for /etc/shadow")

        # Now parse output lines for correctness
        for line in output.splitlines():
            if "-w /etc/shadow" in line:
                match = re.search(r"-p\s*([rwa]+)", line)
                if match:
                    perms = match.group(1)
                    if "w" in perms and "a" in perms:
                        return ("Pass", f"Audit rule is correct: {line}")
                    else:
                        return ("Fail", f"Permissions found but missing 'w' or 'a': {line}")
                else:
                    return ("Fail", f"No -p permissions found in rule: {line}")

        return ("Fail", f"No valid rules found for /etc/shadow: {output}")

    except Exception as e:
        return ("Error", str(e))
print(check_audit_shadow_file())
