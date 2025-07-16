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

        loaded_line = ""
        active_line = ""

        for line in output.splitlines():
            if line.startswith("loaded:"):
                loaded_line = line.strip()
            elif line.startswith("active:"):
                active_line = line.strip()

        if "masked" in loaded_line:
            return ("Pass", "ctrl-alt-del.target is masked as required")
        else:
            return (
                "Fail",
                f"ctrl-alt-del.target is not masked — status is: {loaded_line}; {active_line}"
            )

    except Exception as e:
        return ("Error", str(e))

print(check_ctl_alt_del())
