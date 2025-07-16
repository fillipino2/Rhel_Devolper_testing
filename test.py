import subprocess

def check_signed_packages():
    try:
        result = subprocess.run(
            " grep -E '^\\[.*\\]|gpgcheck' /etc/yum.repos.d/*.repo",
            shell=True,
            capture_output=True,
            text=True 
        )
        for line in result.stdout.splitlines():
            if "gpgcheck" in line:
                if line.strip().endswith("gpgcheck=1"):
                    continue
                else:
                    return "Fail"
        return "Pass"
    except Exception as e:
        return f"Error: {e}"
