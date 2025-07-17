import subprocess
import re
import os
import glob



def check_gui_ctrlaltdel_86():
    try:
        # Step 1: Check if the system is running in GUI mode
        command = subprocess.run(
            ["systemctl", "get-default"],
            capture_output=True,
            text=True
        )

        if command.returncode != 0:
            return ("Error", f"Failed to get default target: {command.stderr.strip()}")

        output = command.stdout.strip()

        if output == "multi-user.target":
            return ("Not Applicable", "System is running in non-GUI (multi-user) mode. Ctrl+Alt+Del GUI logout policy does not apply.")

        # Step 2: Check for logout setting in dconf files (GUI systems only)
        file_paths = glob.glob("/etc/dconf/db/local.d/*")
        found_setting = False

        for file_path in file_paths:
            try:
                with open(file_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            key, val = [x.strip() for x in line.split("=", 1)]
                            if key == "logout":
                                found_setting = True
                                if val == "":
                                    return ("Pass", f"GUI Ctrl+Alt+Del logout is disabled via empty 'logout' setting in: {file_path}")
                                else:
                                    return ("Fail", f"'logout' is set to '{val}' instead of being empty (disabled) in: {file_path}")
            except Exception as read_error:
                continue  # skip unreadable files

        if not found_setting:
            return ("Fail", "No 'logout' setting found in any /etc/dconf/db/local.d/* file. GUI Ctrl+Alt+Del logout may be enabled.")

    except Exception as e:
        return ("Error", str(e))

                
print(check_gui_ctrlaltdel_86())
