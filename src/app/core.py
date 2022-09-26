import traceback
import sys
import logging
from flask import jsonify, request, Blueprint
from utils import create_celery, init_celery
import rdfind
import math

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
    include_rows = request.args.get("rows", "true") == "true"
    task_result = celery.AsyncResult(task_id)
    result = task_result.result

    if task_result.failed():
        result = {
            "error": str(task_result.result),
            "traceback": task_result.traceback,
        }
    if result and "rows" in result and not include_rows:
        del result["rows"]
    res = {"id": task_id, "status": task_result.status, "result": result}
    return jsonify(res)


@bp.route("/tasks/<task_id>/rows", methods=["GET"])
def get_result_paginated(task_id):
    page = int(request.args.get("page", "1"))
    page_size = int(request.args.get("page_size", "100"))

    task_result = celery.AsyncResult(task_id)
    result = task_result.result

    if task_result.failed():
        result = {
            "error": str(task_result.result),
            "traceback": task_result.traceback,
        }
    else:
        rows = result["rows"]
        start = (page - 1) * page_size
        end = page * page_size
        last_page = math.ceil(len(rows) / page_size) or 1
        result = {
            "page": page,
            "next": page + 1 if page < last_page else None,
            "page_size": page_size,
            "last_page": last_page,
            "result": {"rows": rows[start:end]},
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
