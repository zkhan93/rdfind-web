import traceback
import sys
import logging
from flask import jsonify, request, Blueprint
from utils import create_celery, init_celery, read_rows_from
import rdfind
import math
import os

# from app import app, celery

bp = Blueprint("core", __name__, url_prefix="", static_folder="../static")
celery = create_celery()
celery = init_celery(celery, bp)


def error_response():
    _, ex, exc_traceback = sys.exc_info()
    return (
        jsonify(
            dict(
                error=str(ex),
                traceback=traceback.format_tb(exc_traceback),
            )
        ),
        400,
    )


@bp.route("/")
@bp.route("/<file>")
def index(file="index"):
    return bp.send_static_file(f"{file}.html")


@bp.route("/tasks/<task_id>", methods=["GET"])
def get_status(task_id):

    task_result = celery.AsyncResult(task_id)
    result = task_result.result

    if task_result.failed():
        result = {
            "error": str(task_result.result),
            "traceback": task_result.traceback,
        }
    if result and "filename" in result:  # this identifies analysis tasks
        if request.args.get("rows", "true") == "true":
            result["rows"] = read_rows_from(result["filename"], 0, None)
    res = {"id": task_id, "status": task_result.status, "result": result}
    return jsonify(res)


@bp.route("/tasks/<task_id>/rows", methods=["GET"])
def get_result_paginated(task_id):
    page = int(request.args.get("page", "1"))
    page_size = int(request.args.get("page_size", "100"))
    sort_field = request.args.get("sort")

    task_result = celery.AsyncResult(task_id)
    result = task_result.result

    if task_result.failed():
        result = {
            "error": str(task_result.result),
            "traceback": task_result.traceback,
        }
    else:
        filename = "/storage/rdfind-result-test.txt"
        result["filename"] = filename
        start = (page - 1) * page_size
        end = page * page_size
        rows, total_rows = read_rows_from(result["filename"], start, end, sort_field)
        last_page = math.ceil(total_rows / page_size) or 1
        result = {
            "page": page,
            "next": page + 1 if page < last_page else None,
            "page_size": page_size,
            "last_page": last_page,
            "result": {"rows": rows},
        }
    return jsonify(result)


@bp.route("/analyze", methods=["POST"])
def run_rdfind():
    task = rdfind.analyze.delay(request.json)
    return jsonify(dict(task_id=task.id))


@bp.route("/delete-files", methods=["POST"])
def delete_files():
    task = rdfind.delete.delay(request.json)
    return jsonify(dict(task_id=task.id))
