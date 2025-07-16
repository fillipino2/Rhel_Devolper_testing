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
            return ("Fail", f"Gui has been installed {command.stdout} ")
        else:
            return ("Pass", f"No GUI has been installed {command.stdout}")
    except Exception as e:
        return f"Error: {e}"
print(check_gui())
