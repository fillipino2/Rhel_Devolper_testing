import subprocess
import re
import os

def check_ctl_alt_del():
    try:
        command = subprocess.run(
            "systemctl status ctrl-alt-del.target",
            shell=True,
            capture_output=True,
            text=True
        )
        output = command.stdout.strip().lower()

        for line in output.splitlines():
            if line.startswith("loaded:"):
                if "masked" in line:
                    return ("Pass", "ctrl-alt-del.target is masked as required")
                else:
                    return ("Fail", f"ctrl-alt-del.target is not masked: {line.strip()}")

        return ("Fail", "Loaded line not found in systemctl output")

    except Exception as e:
        return ("Error", str(e))

print(check_ctl_alt_del())
