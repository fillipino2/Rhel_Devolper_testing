import subprocess
import re
import os

def check_icmp_redirect():
    try:
        file_list =["/run/sysctl.d/*.conf",
                    "/usr/local/lib/sysctl.d/*.conf",
                    "/usr/lib/sysctl.d/*.conf",
                    "/lib/sysctl.d/*.conf",
                    "/etc/sysctl.conf",
                    "/etc/sysctl.d/*.conf"]
        
        command = subprocess.run("sysctl net.ipv4.conf.all.accept_redirects", shell=True,
                                 capture_output=True,
                                 text=True)
        output = command.stdout.strip()
        if output != "net.ipv4.conf.all.accept_redirects = 0":
            return "Fail"
        files_to_check = []
        for path in file_list:
            if "*" in path:
                files_to_check.extend(glob.glob(path))
            else:
                files_to_check.append(path)

        for file_path in files_to_check:
            try:
                with open(file_path, "r")as fp:
                    for line in fp:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "net.ipv4.conf.all.accept_redirects" in line and "=" in line:
                            key, val = [x.strip() for x in line.split("=", 1)]
                            if key == "net.ipv4.conf.all.accept_redirects" and val != "0":
                                return "Fail"
            except Exception:
                continue
        return "Pass"
    except Exception as e:
            return f"Error: {e}"

print(check_icmp_redirect())
