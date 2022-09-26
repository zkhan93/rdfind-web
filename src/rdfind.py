import subprocess
from celery import shared_task
import time
import csv
import os


@shared_task(name="analyze")
def analyze(params):
    path = params["path"]
    path = os.path.normpath(path)
    if not path.startswith("/storage"):
        return {"error": "location should start with /storage"}
    minsize = str(params["minsize"])
    checksum = params["checksum"]
    ignoreempty = "true" if params.get("ignoreempty", True) else "false"
    timestamp = int(time.time())
    filename = f"{timestamp}_report.txt"
    cp = subprocess.run(
        [
            "rdfind",
            "-minsize",
            minsize,
            "-checksum",
            checksum,
            "-ignoreempty",
            ignoreempty,
            "-outputname",
            filename,
            path,
        ],
        capture_output=True,
    )
    os.system(f"sed -i '1d;$d' {filename}")
    os.system(f"sed -i '1s/^. //' {filename}")
    os.system(f"sed -i 's/\/\(.*\)/\"\/\\1\"/' {filename}")

    return {
        "stdout": cp.stdout.decode(),
        "stderr": cp.stderr.decode(),
        "filename": filename,
    }


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
