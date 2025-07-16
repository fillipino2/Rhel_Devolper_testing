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

        # 1. Check live value
        command = subprocess.run(
            "sysctl net.ipv4.conf.all.accept_redirects",
            shell=True,
            capture_output=True,
            text=True
        )
        output = command.stdout.strip()

        live_pass = output == "net.ipv4.conf.all.accept_redirects = 0"
        file_pass = True
        fail_details = []

        # 2. Expand and check config files
        files_to_check = []
        for path in file_list:
            if "*" in path:
                files_to_check.extend(glob.glob(path))
            else:
                files_to_check.append(path)

        for file_path in files_to_check:
            try:
                with open(file_path, "r") as fp:
                    for line_num, line in enumerate(fp, 1):
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "net.ipv4.conf.all.accept_redirects" in line and "=" in line:
                            key, val = [x.strip() for x in line.split("=", 1)]
                            val = val.split("#")[0].strip().lower()
                            if key == "net.ipv4.conf.all.accept_redirects" and val != "0":
                                file_pass = False
                                fail_details.append(f"{file_path}:{line_num} sets {key} = {val}")
            except Exception:
                continue

        # 3. Combine results
        if not live_pass and not file_pass:
            return ("Fail", f"Live setting wrong: {output}; File issues: {', '.join(fail_details)}")
        elif not live_pass:
            return ("Fail", f"Live setting wrong: {output}")
        elif not file_pass:
            return ("Fail", f"File issues: {', '.join(fail_details)}")
        else:
            return ("Pass", "ICMP redirect is disabled both live and in config")

    except Exception as e:
        return ("Error", str(e))
print(check_icmp_redirect())
