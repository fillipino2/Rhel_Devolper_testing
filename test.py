import subprocess
import re
import os

def check_rsh_server_package():
        try:
            command = subprocess.run("yum list installed  rsh-server",shell=True,capture_output=True,text=True)
        
            if command.returncode == 0:
                return ("Fail", f"rsh-server has been installed and needs to be removed: {command.stdout}")
            else:
                return ("Pass", "rsh-server is not installed")
        except Exception as e:
            return f"Error {e}"

print(check_rsh_server_package())
