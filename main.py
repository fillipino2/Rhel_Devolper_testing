#main python script
import csv
import checklist1
import inspect

check_functions = [
    (name, obj) for name, obj in inspect.getmembers(checklist1)
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
