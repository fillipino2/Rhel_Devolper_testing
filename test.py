import subprocess
import re
import os
import glob

def check_icmp_redirect():
    try:
        file_list = [
            "/run/sysctl.d/*.conf",
            "/usr/local/lib/sysctl.d/*.conf",
            "/usr/lib/sysctl.d/*.conf",
            "/lib/sysctl.d/*.conf",
            "/etc/sysctl.conf",
            "/etc/sysctl.d/*.conf"
        ]

        # Check live value
        command = subprocess.run(
            "sysctl net.ipv4.conf.all.accept_redirects",
            shell=True,
            capture_output=True,
            text=True
        )
        output = command.stdout.strip()

        if output != "net.ipv4.conf.all.accept_redirects = 0":
            return ("Fail", "Live setting is not 0: " + output)

        # Expand all file paths (resolve globs)
        files_to_check = []
        for path in file_list:
            if "*" in path:
                files_to_check.extend(glob.glob(path))
            else:
                files_to_check.append(path)

        # Check each file
        for file_path in files_to_check:
            try:
                with open(file_path, "r") as fp:
                    for line_num, line in enumerate(fp, 1):
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "net.ipv4.conf.all.accept_redirects" in line and "=" in line:
                            key, val = [x.strip() for x in line.split("=", 1)]

                            # Sanitize val to remove inline comments, if any
                            val = val.split("#")[0].strip().lower()

                            if key == "net.ipv4.conf.all.accept_redirects" and val != "0":
                                return ("Fail", f"{file_path}:{line_num} sets {key} = {val}")
            except Exception as e:
                # You could log this if needed
                continue

        return ("Pass", "ICMP redirect is disabled both live and in config")

    except Exception as e:
        return f"Error {e}"
print(check_icmp_redirect())
