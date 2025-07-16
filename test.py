import subprocess
import re
import os

def check_bios_UEFI():
    try:
        firmware = subprocess.run("test -d /sys/firmware/efi && echo UEFI || echo BIOS", shell=True, capture_output=True, text=True)
        if firmware.stdout.strip().lower() == "uefi":
            result = subprocess.run("grep -iw grub2_password /boot/efi/EFI/redhat/user.cfg", shell=True, capture_output=True, text=True)
            output = result.stdout.strip().lower()
            if output.startswith("grub2_password=grub.pbkdf2.sha512"):
                return ("Pass", f"grub2_password is secure: {output}")
            else:
                return ("Fail", f"grub2_password is unsecure: {output}")
        return ("N/A", "Only Applicable to UEFI systems")
    except Exception as e:
        return f"Error: {e}"

print(check_bios_UEFI())
