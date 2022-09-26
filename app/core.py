import traceback
import sys
import logging
from flask import jsonify, request, Blueprint
from utils import create_celery, init_celery
import rdfind

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
    return jsonify(
        {
            "id": task_id,
            "status": task_result.status,
            "result": result,
        }
    )


@bp.route("/analyze", methods=["POST"])
def run_rdfind():
    path = request.json["path"]
    task = rdfind.analyze.delay(path)
    return jsonify(dict(task_id=task.id))


@bp.route("/delete-files", methods=["POST"])
def delete_files():
    task = rdfind.delete.delay(request.json)
    return jsonify(dict(task_id=task.id))
