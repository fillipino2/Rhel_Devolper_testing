import subprocess
import re
import os
import glob


def check_gui_ctrlaltdel_86():
    try:
        # Check if system is running in GUI mode
        command = subprocess.run(["systemctl", "get-default"],
                                 capture_output=True,
                                 text=True)
        output = command.stdout.strip()

        if output == "multi-user.target":
            return "Not Applicable"

        # Check for logout setting in dconf files
        file_paths = glob.glob("/etc/dconf/db/local.d/*")
        for file_path in file_paths:
            try:
                with open(file_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            key, val = [x.strip() for x in line.split("=", 1)]
                            if key == "logout" and val == "":
                                return "Pass"
            except Exception:
                continue  # skip unreadable files

        return "Fail"
    except Exception as e:
        return f"Error: {e}"

                
print(check_gui_ctrlaltdel_86())
