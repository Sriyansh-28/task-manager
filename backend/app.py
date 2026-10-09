"""Task Manager REST API (Flask + MongoDB)."""
import os
from datetime import datetime, timezone

from bson import ObjectId
from flask import Flask, jsonify, request
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError
from werkzeug.exceptions import HTTPException

MAX_TITLE_LENGTH = 200


def serialize(task):
    """Convert a MongoDB document into a JSON-friendly dict."""
    created_at = task.get("created_at")
    if created_at is not None:
        if created_at.tzinfo is None:  # MongoDB returns naive UTC datetimes
            created_at = created_at.replace(tzinfo=timezone.utc)
        created_at = created_at.isoformat()
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "completed": task["completed"],
        "created_at": created_at,
    }


def error(message, status):
    return jsonify({"error": message}), status


def create_app(db=None):
    """Application factory. Tests pass in a mock database via `db`."""
    app = Flask(__name__)

    state = {"db": db}

    def get_tasks():
        """Return the tasks collection, connecting on first use.

        Connecting lazily keeps the app (and /health) up even if the database
        settings are wrong; requests that need the database then return 503.
        """
        if state["db"] is None:
            try:
                client = MongoClient(
                    os.environ.get("MONGO_URI", "mongodb://localhost:27017"),
                    serverSelectionTimeoutMS=5000,
                )
            except PyMongoError:
                raise
            except Exception as exc:  # e.g. a malformed MONGO_URI
                raise PyMongoError(f"Invalid MongoDB configuration: {exc}") from exc
            state["db"] = client[os.environ.get("MONGO_DB_NAME", "taskmanager")]
        return state["db"]["tasks"]

    def parse_id(task_id):
        return ObjectId(task_id) if ObjectId.is_valid(task_id) else None

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/api/tasks")
    def list_tasks():
        return jsonify([serialize(t) for t in get_tasks().find().sort("created_at", -1)])

    @app.post("/api/tasks")
    def create_task():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return error("Request body must be a JSON object.", 400)
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            return error("'title' is required and must be a non-empty string.", 400)
        title = title.strip()
        if len(title) > MAX_TITLE_LENGTH:
            return error(f"'title' must be at most {MAX_TITLE_LENGTH} characters.", 400)

        task = {
            "title": title,
            "completed": False,
            "created_at": datetime.now(timezone.utc),
        }
        task["_id"] = get_tasks().insert_one(task).inserted_id
        return jsonify(serialize(task)), 201

    @app.patch("/api/tasks/<task_id>")
    def update_task(task_id):
        oid = parse_id(task_id)
        if oid is None:
            return error("Invalid task id.", 400)
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or not isinstance(data.get("completed"), bool):
            return error("'completed' is required and must be true or false.", 400)

        task = get_tasks().find_one_and_update(
            {"_id": oid},
            {"$set": {"completed": data["completed"]}},
            return_document=ReturnDocument.AFTER,
        )
        if task is None:
            return error("Task not found.", 404)
        return jsonify(serialize(task))

    @app.delete("/api/tasks/<task_id>")
    def delete_task(task_id):
        oid = parse_id(task_id)
        if oid is None:
            return error("Invalid task id.", 400)
        if get_tasks().delete_one({"_id": oid}).deleted_count == 0:
            return error("Task not found.", 404)
        return "", 204

    @app.errorhandler(PyMongoError)
    def handle_db_error(exc):
        app.logger.error("Database error: %s", exc)
        return error("Database is unavailable. Please try again later.", 503)

    @app.errorhandler(HTTPException)
    def handle_http_error(exc):
        return error(exc.description, exc.code)

    return app


if __name__ == "__main__":
    create_app().run(
        host=os.environ.get("FLASK_HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
    )
