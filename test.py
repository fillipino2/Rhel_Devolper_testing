import subprocess
import re

def check_crypto_policies():
    try:
        result = subprocess.run("update-crypto-policies --show", shell=True, capture_output=True, text=True)
        output = result.stdout.lower().strip()
        if output == "future":
            return "Pass"
        else:
            return "Fail"
    except Exception as e:
        return f"Error: {e}"

print(check_crypto_policies())
