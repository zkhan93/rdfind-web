import subprocess
from celery import shared_task
import time
import csv
import os


@shared_task(name="analyze")
def analyze(path):
    path = os.path.normpath(path)
    if not path.startswith("/storage"):
        return {"error": "location should start with /storage"}
    timestamp = int(time.time())
    filename = f"{timestamp}_report.txt"
    cp = subprocess.run(["rdfind", "-outputname", filename, path], capture_output=True)

    # strip first and last line from result file
    os.system(f"sed -i '1d;$d' {filename}")
    os.system(f"sed -i '1s/^. //' {filename}")
    os.system(f"sed -i 's/\/\(.*\)/\"\/\\1\"/' {filename}")

    rows = []

    with open(filename, "r") as res:
        reader = csv.DictReader(
            res,
            delimiter=" ",
            quotechar='"',
        )
        for index, row in enumerate(reader):
            row["key"] = index
            row["duptype"] = {
                "DUPTYPE_FIRST_OCCURRENCE": "FIRST",
                "DUPTYPE_WITHIN_SAME_TREE": "DUPE",
            }[row["duptype"]]
            rows.append(row)
    os.remove(filename)
    return {"stdout": cp.stdout.decode(), "stderr": cp.stderr.decode(), "rows": rows}


@shared_task(name="delete-files")
def delete(files):
    deleted = []
    errored = []
    for file in files:
        try:
            path = os.path.normpath(file)
            if path.startswith("/storage"):
                os.remove(path)
                deleted.append(path)
            else:
                raise Exception("files should start with /storage")
        except Exception as ex:
            errored.append(dict(file=file, error=str(ex)))
    return {"deleted": deleted, "errored": errored}
