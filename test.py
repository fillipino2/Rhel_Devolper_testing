import subprocess
import re
import os

def check_telnet_server_package():
    try:
        command = subprocess.run("yum list installed telnet-server",shell=True,capture_output=True,text=True)
        
        if command.returncode != 0:
            return ("Pass", "No telnet-server package is installed")
        else:
            return ("Fail", "telnet-server package is installed and must be removed")
    except Exception as e:
        return f"Error {e}"

print(check_telnet_server_package())
