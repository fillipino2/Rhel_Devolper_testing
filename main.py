#main python script
import csv
import inspect
import importlib
import shutil
import os


def check_ocp_or_rhel():
    return(
        shutil.which("oc") is not None or
        shutil.which("kubectl") is not None or
        os.path.isdir("/run/secrets/kubernetes.io") or
        os.getenv("KUBERNETES_SERVICE_HOST") is not None
    )

os_environment = "ocp_checklist" if check_ocp_or_rhel() else "checklist"

import_checklist = importlib.import_module(os_environment)
check_functions = [
    (name, obj) for name, obj in inspect.getmembers(import_checklist)
    if inspect.isfunction(obj) and name.startswith("check_")
    
]

numb_of_checks = len(check_functions)


with open("result.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Check Name", "Result", "Details"])

    for name, func in check_functions:
        try:
            result = func()

            if isinstance(result, str):
                if result.lower().startswith("pass"):
                    writer.writerow([name, "Pass", result])
                else:
                    writer.writerow([name, "Fail", result])

            elif isinstance(result, tuple) and len(result) >= 1:
                status = result[0]
                details = result[1] if len(result) > 1 else ""
                writer.writerow([name, status, details])

            elif result is True:
                writer.writerow([name, "Pass", ""])
            else:
                writer.writerow([name, "Fail", str(result)])

        except Exception as e:
            writer.writerow([name, "Error", str(e)])
