import subprocess

def check_077():
    try:
        files = ["/etc/bashrc", "/etc/csh.cshrc", "/etc/profile"]
        command = subprocess.run(["grep", "-i", "umask"] + files, capture_output=True, text=True)

        if command.returncode != 0:
            return ("Fail", "No 'umask' entries found in target files")

        lines = command.stdout.strip().splitlines()
        failures = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("#"):
                failures.append(f"Commented out: {stripped}")
                continue

            if "077" in stripped:
                continue  # correct setting
            elif "022" in stripped or "umask" in stripped:
                failures.append(f"Insecure or unexpected setting: {stripped}")

        if failures:
            return ("Fail", "; ".join(failures))
        else:
            return "Pass"

    except Exception as e:
        return ("Error", str(e))
