# api.py

from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from models import Task, db

api = Blueprint("api", __name__)

# Helper: Convert Task model to dict
def task_to_dict(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "user_id": task.user_id
    }

# GET all tasks for the current user
@api.route("/api/tasks", methods=["GET"], strict_slashes=False)
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify([task_to_dict(task) for task in tasks]), 200

# GET a specific task
@api.route("/api/tasks/<int:task_id>", methods=["GET"], strict_slashes=False)
@login_required
def get_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task_to_dict(task)), 200

# POST a new task
@api.route("/api/tasks", methods=["POST"])
@login_required
def create_task():
    data = request.get_json()
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if len(title) > 200:
        return jsonify({"error": "Title is too long"}), 400

    new_task = Task(title=title, description=description, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return jsonify(task_to_dict(new_task)), 201

# PUT to update a task
@api.route("/api/tasks/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.completed = data.get("completed", task.completed)
    db.session.commit()
    return jsonify(task_to_dict(task)), 200

# DELETE a task
@api.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200
