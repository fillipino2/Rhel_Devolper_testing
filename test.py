
import subprocess
import re
import glob
import os

# def umask_077():
#     with open("/etc/login.defs", "r") as umask:

# V-230385
def check_077():
    try:
        files = ["/etc/bashrc", "/etc/csh.cshrc", "/etc/profile"]
        command = subprocess.run(["grep", "-Hi", "umask"] + files, capture_output=True, text=True)

        if command.returncode != 0 or not command.stdout.strip():
            return ("Fail", "No 'umask' entries found in /etc/bashrc, /etc/csh.cshrc, or /etc/profile")

        failures = []

        for line in command.stdout.strip().splitlines():
            # grep with -H gives output like: /etc/bashrc:umask 022
            parts = line.split(":", 1)
            if len(parts) != 2:
                continue
            filename, content = parts
            stripped = content.strip()

            if stripped.startswith("#"):
                failures.append(f"{filename.strip()}: umask commented out")
            elif "077" in stripped:
                continue  # Secure
            elif "umask" in stripped:
                failures.append(f"{filename.strip()}: {stripped}")

        if failures:
            return ("Fail", "; ".join(failures))
        else:
            return ("Pass", "umask 077 is correctly set in all checked files")

    except Exception as e:
        return ("Error", str(e))



# V-230264
def check_gpgcheck_enabled():
    try:
        result = subprocess.run(
            r"grep -E '^\[.*\]|^[[:space:]]*gpgcheck' /etc/yum.repos.d/*.repo",
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return ("Fail", "No gpgcheck settings found in .repo files")

        section = None
        failures = []

        for line in result.stdout.strip().splitlines():
            line = line.strip()

            if line.startswith("[") and line.endswith("]"):
                section = line
                continue

            # Skip comments
            if line.startswith("#") or not line:
                continue

            # Match gpgcheck lines
            match = re.match(r"gpgcheck\s*=\s*(\d)", line)
            if match:
                value = match.group(1)
                if value != "1":
                    failures.append(f"{section or 'unknown section'}: gpgcheck={value}")
            else:
                # gpgcheck line not in proper format
                failures.append(f"{section or 'unknown section'}: malformed gpgcheck line")

        if failures:
            return ("Fail", "; ".join(failures))
        else:
            return ("Pass", "All gpgcheck settings are enabled")

    except Exception as e:
        return ("Error", str(e))
# V-230265    
def check_signed_packages_dnf():
    try:
        with open("/etc/dnf/dnf.conf", "r") as dnf:
            for line in dnf:
                line = line.strip()
                if line.startswith("localpkgcheck_gpg"):
                    key_value = [s.strip() for s in line.split("=", 1)]
                    if len(key_value) == 2 and key_value[1].lower() == "true":
                        return ("Pass", "'localpkgcheck_gpg=true' is set correctly")
                    else:
                        return ("Fail", f"Found 'localpkgcheck_gpg={key_value[1]}', expected 'true'")
        # If the loop finishes and no match was found
        return ("Fail", "'localpkgcheck_gpg=true' is missing from /etc/dnf/dnf.conf")

    except Exception as e:
        return ("Error", str(e))
    
# V-230282   
def check_selinux_enabled():
    try:
        result = subprocess.run(["sestatus"], capture_output=True, text=True)
        output = result.stdout.lower()

        for line in output.splitlines():
            if line.startswith("selinux status:"):
                status = line.split(":", 1)[1].strip()
                if status == "enabled":
                    return ("Pass", "SELinux is enabled")
                else:
                    return ("Fail", f"SELinux is {status}")
        return ("Fail", "SELinux status line not found")

    except Exception as e:
        return ("Error", str(e))

# V-230282   
def check_selinux_target_policy():
    try:
        command = subprocess.run(["sestatus"], capture_output=True,text=True)
        output = command.stdout.lower()
        for line in output.splitlines():
            if line.startswith("loaded policy name:"):
                status = line.split(":", 1)[1].strip()
                if status == "targeted":
                    return ("Pass", "SELinux is enforcing targeted policies")
                else:
                    return ("Fail", f"SELinux is {status}")
        return ("Fail", "SELinux loaded policy name was not found")
    except Exception as e:
        return ("Error", str(e))



#V-251706   
def check_blank_password():
    try:

        empty_user = []
        with open("/etc/shadow", "r") as empty:
            for line in empty:
                fields = line.strip().split(":")
                if len(fields) > 1 and fields[1] == "":
                    empty_user.append(fields[0])
        if empty_user:
            return ("Fail", f"Users with blank passwords: {', '.join(empty_user)}")
        else:
            return ("Pass", "No empty passwords for users")
    except Exception as e:
        return ("Error", str(e))
    

# Ensure System is using Updated Crpytography
def check_crypto_policies():
    try:
        result = subprocess.run("update-crypto-policies --show", shell=True, capture_output=True, text=True)
        output = result.stdout.lower().strip()
        if output == "future":
            return ("Pass", "Crypro policies are set to use only secure algorithms")
        else:
            return ("Fail", f"Crypto policies allow unsecure algorithms: {output}")
    except Exception as e:
        return f"Error: {e}"

# V-230329
def check_auto_login_with_gui():
    path = "/etc/gdm/custom.conf"
    if not os.path.exists(path):
        return ("N/A", "custom.conf is not present; GUI is most likely not in use, Ask stakeholder to configr")
    
    try:

        with open("/etc/gdm/custom.conf", "r") as auto:
         
            for line in auto:
                line = line.strip().lower()
                if line.startswith("automaticloginenable"):
                    if "#" in line or ";" in line:
                        continue
                    value = line.split("=", 1)[1].strip()
                    return "Pass" if value == "false" else "fail"
        return "Fail"
    except Exception as e:
        return f"Error: {e}"

def check_bios_UEFI():
    try:
        firmware = subprocess.run("test -d /sys/firmware/efi && echo UEFI || echo BIOS", shell=True, capture_output=True, text=True)
        if firmware.stdout.strip().lower() == "uefi":
            result = subprocess.run("grep -iw grub2_password /boot/efi/EFI/redhat/user.cfg", shell=True, capture_output=True, text=True)
            output = result.stdout.strip().lower()
            if output.startswith("grub2_password=grub.pbkdf2.sha512"):
                return ("Pass", f"grub2_password is secure: {output}")
            else:
                return ("Fail", f"grub2_password is unsecure: {output}")
        return ("N/A", "Only Applicable to UEFI systems")
    except Exception as e:
        return f"Error: {e}"

 # V-230529   
def check_ctl_alt_del():
    try:
        command = subprocess.run(
            "systemctl status ctrl-alt-del.target",
            shell=True,
            capture_output=True,
            text=True
        )
        output = command.stdout.strip().lower()

        for line in output.splitlines():
            if line.lstrip().startswith("loaded:"):
                if "masked" in line:
                    return ("Pass", "ctrl-alt-del.target is masked as required")
                else:
                    return ("Fail", f"ctrl-alt-del.target is not masked: {line.strip()}")

        return ("Fail", "Loaded line not found in systemctl output")

    except Exception as e:
        return ("Error", str(e))
    
#    V-230221
def check_os_release(min_required_version="8.10"):
    try:
        command = subprocess.run("sudo cat /etc/redhat-release", shell=True, capture_output=True, text=True)
        result = command.stdout.strip()
        match = re.search(r'release\s+(\d+\.\d+)', result.lower())
        if not match:
            return "Fail"
        current_version = float(match.group(1))
        required_version = float(min_required_version)
        if current_version >= required_version:
            return ("Pass", f"The version is the correct version: {current_version}")
        else:
            return ("Fail", f"The version does not meet the required version: {current_version}")
        
    except Exception as e:
        return f"Error: {e}"
    
# V-230534 Will work on this later

# V-230487
def check_telnet_server_package():
    try:
        command = subprocess.run("yum list installed telnet-server",shell=True,capture_output=True,text=True)
        
        if command.returncode != 0:
            return ("Pass", "No telnet-server package is installed")
        else:
            return ("Fail", "telnet-server package is installed and must be removed")
    except Exception as e:
        return f"Error {e}"

# V-244542
def check_audit_services():
    try:
        command = subprocess.run("systemctl status auditd.service", shell=True, capture_output=True, text=True)
        output = command.stdout.strip()
        for line in output.splitlines():
            if line.lstrip().startswith("Active:"):
                    if "active (running)" in line.lower():
                        return ("Pass", "Audit service is currently running")
                    else:
                        return ("Fail", "Audit service is not currently running")
    except Exception as e:
        return f"Error: {e}"
# V-230284
def check_shosts_file():
    try:
        command = subprocess.run("find / -name '*.shosts' 2>/dev/null", shell=True, capture_output=True, text=True)
        output = command.stdout.strip()
        if output:
            return ("Fail", f"shosts files were found: {command.stdout}")
        else:
            return ("Pass", "No .shosts file was found")
    except Exception as e:
        return f"Error: {e}"
    
# V-230558
def check_ftp_package():
    try:
        command = subprocess.run("sudo yum list installed | grep ftpd", shell=True, capture_output=True, text=True)
        if command.returncode == 0:
            return ("Fail", f"ftpd package was found: {command.stdout}")
        else:
            return ("Pass", "No ftpd package was found was found")
    except Exception as e:
        return f"Error: {e}"

# V-230492
def check_rsh_server_package():
        try:
            command = subprocess.run("yum list installed  rsh-server",shell=True,capture_output=True,text=True)
        
            if command.returncode == 0:
                return ("Fail", f"rsh-server has been installed and needs to be removed: {command.stdout}")
            else:
                return ("Pass", "rsh-server is not installed")
        except Exception as e:
            return f"Error {e}"

# V-230380
def check_permitemptypassword_sshd():
    try:
        with open("/etc/ssh/sshd_config", "r") as permitpasswd:
            for line in permitpasswd:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue
                
                if line.lower().startswith("permitemptypassword"):
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].lower() == "no":
                        return ("PermitEmptyPasswords", "pass", "set to no")
                    else:
                        return ("PermitEmptyPasswords", "Fail", f"{parts[1] if len(parts) > 1 else 'missing'}")
        return (" PermitEmptyPasswords", "Pass", "Directive not found")
    except Exception as e:
        return ("PermitEmptyPasswords", "error", str(e))
    
#V-230283
def check_shosts_equiv_file():
    try:
        command = subprocess.run("find / -name '*.shosts.equiv' 2>/dev/null", shell=True, capture_output=True, text=True)
        output = command.stdout.strip()
        if output:
            return ("Fail", f"shosts.equiv file was found: {command.stdout}")
        else:
            return ("Pass", "No shosts.equiv file was found")
    except Exception as e:
        return f"Error: {e}"
# Need to work on logic and verifiy the output status when command is ran    V-244553 # not getting the apporiate output not telling which file path has the issue
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
    
# still need to do all icmp stuff

# V-230554
def check_promisc_mode():
    try:
        command = subprocess.run("sudo ip link | grep -i promisc", shell=True, capture_output=True, text=True)
        output = command.stdout.strip()
        if output:
            return ("Fail", f"promisc mode is enabled and needs to be turned off: {output}")
        else:
            return ("Pass", "promisc mode is disabled")
    except Exception as e:
        return f"Error: {e}"

# V-230550
def check_postfix():
    try:
        command = subprocess.run("yum list installed postfix",
                                 shell=True,
                                 capture_output=True,
                                 text=True)
        if command.returncode != 0:
            return ("N/A", "Since postifix is not installed this is N/A")
        
        config_check = subprocess.run("postconf -n smtpd_client_restrictions",
                                      shell=True,
                                      capture_output=True,
                                      text=True)
        if config_check.returncode != 0:
            return "Not Applicable"
        
        output = config_check.stdout.strip()

        if "smtpd_client_restrictions" in output and "=" in output:
            key, val = [x.strip() for x in output.split("=",1)]
            if key == "smtpd_client_restrictions" and val == "permit_mynetworks, reject":
                return "Pass"
            else:
                return "Fail"
    except Exception as e:
        return f"Error {e}"
    
 #  V-250317 # this would need some work similiar to the same problomes from above
def check_ipv4_forwarding():
    try:
        file_list =["/run/sysctl.d/*.conf",
                    "/usr/local/lib/sysctl.d/*.conf",
                    "/usr/lib/sysctl.d/*.conf",
                    "/lib/sysctl.d/*.conf",
                    "/etc/sysctl.conf",
                    "/etc/sysctl.d/*.conf"]
        
        command = subprocess.run("sysctl sysctl net.ipv4.conf.all.forwarding", shell=True,
                                 capture_output=True,
                                 text=True)
        output = command.stdout.strip()
        if output != "sysctl net.ipv4.conf.all.forwarding = 0":
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
                        if "sysctl net.ipv4.conf.all.forwarding" in line and "=" in line:
                            key, val = [x.strip() for x in line.split("=", 1)]
                            if key == "sysctl net.ipv4.conf.all.forwarding" and val != "0":
                                return "Fail"
            except Exception:
                continue
        return "Pass"
    except Exception as e:
            return f"Error: {e}"
# V-230540   # same things as one above
def check_ipv4_forwarding():
    try:
        file_list =["/run/sysctl.d/*.conf",
                    "/usr/local/lib/sysctl.d/*.conf",
                    "/usr/lib/sysctl.d/*.conf",
                    "/lib/sysctl.d/*.conf",
                    "/etc/sysctl.conf",
                    "/etc/sysctl.d/*.conf"]
        
        command = subprocess.run("sysctl sysctl net.ipv6.conf.all.forwarding", shell=True,
                                 capture_output=True,
                                 text=True)
        output = command.stdout.strip()
        if output != "sysctl net.ipv6.conf.all.forwarding = 0":
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
                        if "sysctl net.ipv6.conf.all.forwarding" in line and "=" in line:
                            key, val = [x.strip() for x in line.split("=", 1)]
                            if key == "sysctl net.ipv6.conf.all.forwarding" and val != "0":
                                return "Fail"
            except Exception:
                continue
        return "Pass"
    except Exception as e:
            return f"Error: {e}"

# V-230553
def check_gui():

    try:
        command = subprocess.run("rpm -qa | grep xorg | grep server",
                                 shell=True,
                                 capture_output=True,
                                 text=True)
        if command.returncode == 0:
            return ("Fail", f"Gui has been installed {command.stdout} ")
        else:
            return ("Pass", f"No GUI has been installed {command.stdout}")
    except Exception as e:
        return f"Error: {e}"
    
# V-230274
def check_pki_status():
    
    try:

        command = subprocess.run("grep certificate_verification /etc/sssd/sssd.conf /etc/sssd/conf.d/*.conf | grep -v \"^#\"",
                                 shell=True,
                                 capture_output=True,
                                 text=True,)
        if command.returncode == 0:
            output = command.stdout.strip()
            if "=" in output:
                key, val = [x.strip() for x in output.split("=", 1)]
                if key == "certificate_verification" and val == "ocsp_dgst=sha1":
                    return ("Pass", f"Im not sure what to write: {output}")
                else:
                    return ("Fail", f"Im not sure what to write: {output}")
        else:
            return ("Fail", f"but why {output}")
    except Exception as e:
        return f"Error: {e}"

# V-230404
def check_audit_shadow_file():
    try:
        command = subprocess.run(
            "grep /etc/shadow /etc/audit/audit.rules",
            shell=True,
            capture_output=True,
            text=True
        )

        output = command.stdout.strip()

        if command.returncode == 2:
            # Actual error (e.g., file not found)
            return ("Error", f"Grep error: {command.stderr.strip()}")

        if command.returncode == 1 or not output:
            # No match found
            return ("Fail", "No audit rule found for /etc/shadow")

        # Now parse output lines for correctness
        for line in output.splitlines():
            if "-w /etc/shadow" in line:
                match = re.search(r"-p\s*([rwa]+)", line)
                if match:
                    perms = match.group(1)
                    if "w" in perms and "a" in perms:
                        return ("Pass", f"Audit rule is correct: {line}")
                    else:
                        return ("Fail", f"Permissions found but missing 'w' or 'a': {line}")
                else:
                    return ("Fail", f"No -p permissions found in rule: {line}")

        return ("Fail", f"No valid rules found for /etc/shadow: {output}")

    except Exception as e:
        return ("Error", str(e))

# V-230267

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
        return ("Error", str(e))
    
# V-230268

def check_access_hardlinks():
    try:
        # Step 1: Check runtime sysctl value
        command = subprocess.run(
            ["sysctl", "fs.protected_hardlinks"],
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
            return ("Fail", f"fs.protected_hardlinks is not set to '1' at runtime: {output}")

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
                            if "fs.protected_hardlinks" in line and "=" in line:
                                k, v = [x.strip() for x in line.split("=", 1)]
                                if k == "fs.protected_hardlinks" and v == "1":
                                    if directory == "/etc/sysctl.d":
                                        etc_found = f"{file_path}: {line}"
                                    else:
                                        other_found.append(f"{file_path}: {line}")
                except Exception:
                    continue  # silently skip unreadable files

        # Step 3: Determine final result
        if not etc_found:
            return ("Fail", "Runtime setting is correct, but /etc/sysctl.d/* does not set fs.protected_hardlinks = 1")

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
                f"fs.protected_hardlinks is set to '1' at runtime and correctly configured in /etc/sysctl.d:\n{etc_found}"
            )

    except Exception as e:
        return ("Error", str(e))

# V-230531
def check_ctrlaltdelete_burst():
    try:
        with open("/etc/systemd/system.conf", "r") as output:
            for line in output:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue  # skip empty or commented lines

                if "CtrlAltDelBurstAction" in line and "=" in line:
                    key, val = [x.strip() for x in line.split("=", 1)]
                    if key == "CtrlAltDelBurstAction":
                        if val == "none":
                            return ("Pass", f"CtrlAltDelBurstAction is correctly set to 'none' in /etc/systemd/system.conf: {line}")
                        else:
                            return ("Fail", f"CtrlAltDelBurstAction is set to '{val}' instead of 'none' in /etc/systemd/system.conf: {line}")

        return ("Fail", "CtrlAltDelBurstAction setting not found in /etc/systemd/system.conf")

    except Exception as e:
        return ("Error", str(e))

# V-230530        


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
    
    

