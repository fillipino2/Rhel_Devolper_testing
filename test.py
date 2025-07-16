import subprocess
import re

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
