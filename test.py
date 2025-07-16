#plancing test functions to ensure validity and no false positives or false negatives
def check_umask_077():
    result = subprocess.run(["grep", "-i", "umask","/etc/login.defs"], capture_output=True, text=True )
    for line in result.stdout.splitlines():
        if line.strip().startswith("#"):
            continue
        if not "077" in line:
            return ("Fail", f"insecure line {line.strip()}")
    return "Pass"
