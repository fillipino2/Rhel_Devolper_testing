import subprocess
import re
import os
import glob


def check_access_symlinks():
    try:
        # Step 1: Check runtime value
        command = subprocess.run(
            ["sysctl", "fs.protected_symlinks"],
            capture_output=True,
            text=True
        )

        if command.returncode != 0:
            return ("Fail", "Failed to read runtime setting from sysctl")

        output = command.stdout.strip()
        if "=" not in output:
            return ("Fail", f"Unexpected sysctl output: {output}")

        key, val = [x.strip() for x in output.split("=", 1)]
        if key != "fs.protected_symlinks" or val != "1":
            return ("Fail", f"fs.protected_symlinks is not set to '1' at runtime: {output}")

        # Step 2: Only check /etc/sysctl.d/*.conf for persistent config
        found_config = None
        config_files = glob.glob("/etc/sysctl.d/*.conf")

        for file_path in config_files:
            try:
                with open(file_path, "r") as fp:
                    for line in fp:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "fs.protected_symlinks" in line and "=" in line:
                            k, v = [x.strip() for x in line.split("=", 1)]
                            if k == "fs.protected_symlinks" and v == "1":
                                found_config = f"{file_path}: {line}"
                                break
            except Exception:
                continue  # silently skip unreadable files

        if found_config:
            return ("Pass", f"fs.protected_symlinks is correctly set to '1' at runtime and in: {found_config}")
        else:
            return ("Fail", "fs.protected_symlinks = 1 is not set persistently in /etc/sysctl.d/*.conf")

    except Exception as e:
        return ("Error", str(e))
print(check_access_symlinks())
