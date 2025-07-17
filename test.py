import subprocess
import re
import os
import glob


def check_access_symlinks():
    try:
        # Step 1: Check current runtime value
        command = subprocess.run(["sysctl", "fs.protected_symlinks"],
                                 capture_output=True,
                                 text=True)

        if command.returncode != 0:
            return ("Fail", "Failed to query sysctl fs.protected_symlinks")

        output = command.stdout.strip()

        if "=" not in output:
            return ("Fail", f"Unexpected sysctl output format: {output}")

        key, val = [x.strip() for x in output.split("=", 1)]

        if key != "fs.protected_symlinks" or val != "1":
            return ("Fail", f"fs.protected_symlinks is not set to 1 at runtime: {output}")

        # Step 2: Check persistent configuration
        file_list = [
            "/run/sysctl.d/*.conf",
            "/usr/local/lib/sysctl.d/*.conf",
            "/usr/lib/sysctl.d/*.conf",
            "/lib/sysctl.d/*.conf",
            "/etc/sysctl.conf",
            "/etc/sysctl.d/*.conf"
        ]
        files_to_check = []
        for path in file_list:
            if "*" in path:
                files_to_check.extend(glob.glob(path))
            else:
                files_to_check.append(path)

        found_config = None

        for file_path in files_to_check:
            try:
                with open(file_path, "r") as fp:
                    for line in fp:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "fs.protected_symlinks" in line and "=" in line:
                            k, v = [x.strip() for x in line.split("=", 1)]
                            if k == "fs.protected_symlinks":
                                if v == "1":
                                    found_config = f"{file_path}: {line}"
                                    break
            except Exception:
                continue  # silently skip unreadable files

        if found_config:
            return ("Pass", f"fs.protected_symlinks is set to '1' at runtime and persistently configured in {found_config}")
        else:
            return ("Fail", "Runtime setting is correct, but no persistent configuration for fs.protected_symlinks = 1 was found")

    except Exception as e:
        return ("Error", str(e))
print(check_access_symlinks())
