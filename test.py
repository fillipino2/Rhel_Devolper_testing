import subprocess
import re
import os
import glob

def check_gui():

    try:
        command = subprocess.run("rpm -qa | grep xorg | grep server",
                                 shell=True,
                                 capture_output=True,
                                 text=True)
        if command.returncode == 0:
            return "Fail, Unless approved previously"
        else:
            return "Pass"
    except Exception as e:
        return f"Error: {e}"
print(check_gui())
