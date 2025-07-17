import subprocess
import re
import os
import glob

def check_access_symlinks():
    try:

        command = subprocess.run(["sysctl", "fs.protected_symlinks"],
                                 capture_output=True,
                                 text=True)
        if command.returncode != 0:
            return "Fail"

        output = command.stdout.strip()
        if "=" not in output:
            return "Fail"

        key, val = [x.strip() for x in output.split("=", 1)]
        if key != "fs.protected_symlinks" or val != "1":
            return "Fail"


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

        for file_path in files_to_check:
            try:
                with open(file_path, "r") as fp:
                    for line in fp:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "fs.protected_symlinks" in line and "=" in line:
                            key, val = [x.strip() for x in line.split("=", 1)]
                            if key == "fs.protected_symlinks":
                                if val == "1":
                                    return "Pass"
                                else:
                                    return "Fail"
            except Exception:
                continue  # skip unreadable files

        return "Fail"  # No valid persistent config found

    except Exception as e:
        return f"Error: {e}"
print(check_access_symlinks())
