import subprocess
import re
import os
import glob


def check_access_symlinks():
    try:
        # Step 1: Check runtime sysctl value
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

        # Step 2: Check all directories for persistent config
        persistent_dirs = {
            "/etc/sysctl.d": [],
            "/run/sysctl.d": [],
            "/usr/local/lib/sysctl.d": [],
            "/usr/lib/sysctl.d": [],
            "/lib/sysctl.d": [],
        }

        etc_found = None
        other_found = []

        for directory, results in persistent_dirs.items():
            config_files = glob.glob(os.path.join(directory, "*.conf"))
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
                                    if directory == "/etc/sysctl.d":
                                        etc_found = f"{file_path}: {line}"
                                    else:
                                        other_found.append(f"{file_path}: {line}")
                except Exception:
                    continue  # silently skip unreadable files

        # Step 3: Determine final result
        if not etc_found:
            return ("Fail", "Runtime setting is correct, but /etc/sysctl.d/* does not set fs.protected_symlinks = 1")

        if other_found:
            warning = "\n".join(other_found)
            return (
                "Pass",
                f"fs.protected_symlinks is set to '1' at runtime and in /etc/sysctl.d:\n{etc_found}\n"
                f"However, it is also configured in other locations (may cause override issues):\n{warning}"
            )
        else:
            return (
                "Pass",
                f"fs.protected_symlinks is set to '1' at runtime and correctly configured in /etc/sysctl.d:\n{etc_found}"
            )

    except Exception as e:
        return ("Error", str(e)
                
print(check_access_symlinks())
