from flask import request, jsonify, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Task
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
from markupsafe import escape
import re #Email Auth
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# Show homepage
@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("tasks"))
    return render_template("index.html")
    
# Register Route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = escape(request.form.get("username")).strip()
        email = escape(request.form.get("email")).strip()
        password = request.form.get("password")

        if not username or not email or not password:
            return "All fields are required", 400

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return "Invalid email format", 400

        if len(password) < 6:
            return "Password must be at least 6 characters long", 400

        if User.query.filter_by(username=username).first():
            return "Username already exists", 400
        if User.query.filter_by(email=email).first():
            return "Email already exists", 400

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None  # Initialize error message
    if request.method == "POST":
        username = escape(request.form.get("username")).strip()
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        fake_hash = generate_password_hash("fakepassword")  # Dummy hash
        check_password_hash(user.password if user else fake_hash, password)

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("tasks"))  # Redirect to tasks page if login is successful

        error = "Invalid username or password"  # Set error message if login fails

    return render_template("login.html", error=error)


# Logout Route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# Show the task page with all tasks
@app.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():
    if request.method == "POST":
        title = escape(request.form.get("title"))
        description = escape(request.form.get("description", ""))

        if not title:
            return "Task title is required", 400

        if len(title) > 200:
            return "Task title is too long", 400

        if len(description) > 500:
            return "Task description is too long", 400

        new_task = Task(title=title, description=description, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()

        return redirect(url_for("tasks"))  # Refresh the page

    user_tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.id.asc()).all()
    return render_template("tasks.html", tasks=user_tasks)

# Handle task updates (mark as completed)
@app.route("/tasks/<int:task_id>", methods=["POST"])
@login_required
def update_or_delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

    if not task:
        return "Task not found", 404

    method = request.form.get("_method")

    if method == "PUT":
        # Check if this is a "completed" checkbox or an actual edit form
        if "title" in request.form:
            # Handle full task edit (title + description)
            task.title = escape(request.form.get("title"))
            task.description = escape(request.form.get("description", ""))
        else:
            # Handle completed checkbox
            task.completed = request.form.get("completed") == "on"

        db.session.commit()

    elif method == "DELETE":
        db.session.delete(task)
        db.session.commit()

    return redirect(url_for("tasks"))
