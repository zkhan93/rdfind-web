import logging
import os
from celery import Celery
import csv
from collections import defaultdict

logging.basicConfig(level=logging.INFO)


def create_celery():
    celery = Celery("celery app")
    config_from_env = {
        k.split("CELERY_", 1)[1].lower(): v
        if v not in ("True", "False")
        else v == "True"
        for k, v in os.environ.items()
        if k.startswith("CELERY_")
    }
    config = {
        "broker_url": os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
        "result_backend": os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1"),
        "task_time_limit": int(os.getenv("TASK_TIME_LIMIT", "6")),
        "task_ignore_result": False,
        "task_acks_late": True,
        "task_reject_on_worker_lost": True,
    }
    config.update(config_from_env)
    celery.conf.update(config)
    logging.info(f"Celery configured with {config}")

    return celery


def init_celery(celery, app):
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def read_rows_from(filename, start, end, sort_by):
    reverse = False
    if sort_by:
        if sort_by.startswith("-"):
            reverse = True
            sort_by = sort_by[1:]

    with open(filename, "r") as res:
        reader = csv.DictReader(
            res,
            delimiter=" ",
            quotechar='"',
        )
        rows = reader
        if sort_by:
            type_map = defaultdict(lambda: str)
            type_map["size"] = int
            rows = sorted(
                reader, key=lambda x: type_map[sort_by](x[sort_by]), reverse=reverse
            )
        else:
            rows = list(reader)
        row_count = len(rows)
        page_rows = []
        print(start, end)
        for index, row in enumerate(rows[start:end]):
            row["key"] = index + start
            row["duptype"] = {
                "DUPTYPE_FIRST_OCCURRENCE": "FIRST",
                "DUPTYPE_WITHIN_SAME_TREE": "DUPE",
            }[row["duptype"]]
            page_rows.append(row)
        return page_rows, row_count
