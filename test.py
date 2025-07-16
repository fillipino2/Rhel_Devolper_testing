import subprocess
import re

def check_blank_password():
    empty_user = []
    with open("/etc/shadow", "r") as empty:
        for line in empty:
            fields = line.strip().split(":")
            if len(fields) > 1 and fields[1] == "":
                empty_user.append(fields[0])
    if empty_user:
        return ",".join(empty_user)
    else:
        return ("Pass", "No empty passwords for users")

print(check_blank_password())
