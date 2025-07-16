import subprocess

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
