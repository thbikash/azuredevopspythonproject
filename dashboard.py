from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User , WorkflowRun
from github_api import trigger_workflow, get_workflow_runs

# --- Flask app ---
app = Flask(__name__, template_folder="dashboard_templates", static_folder="dashboard_templates/static")
app.secret_key = "devkey123"  # required for Flask-Login session management
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dashboard_users.db"
db.init_app(app)

# --- Flask-Login setup ---
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Authentication routes ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("index"))
        return "<p>Invalid credentials</p><a href='/login'>Try again</a>"
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return "<p>Email already exists</p><a href='/register'>Try again</a>"

        # Create and save new user
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return "<p>Registration successful!</p><a href='/login'>Go to Login</a>"

    return render_template("register.html")


# --- Dashboard / CI/CD routes ---
@app.route("/")
@login_required
def index():
    return render_template("index.html", user=current_user)

@app.route("/trigger-ci", methods=["POST"])
@login_required
def trigger_ci():
    branch = request.form.get("branch")
    status, text = trigger_workflow("ci.yml", inputs={"branch": branch})
    # Save workflow run for current user
    from models import WorkflowRun, db
    run = WorkflowRun(user_id=current_user.id, workflow="ci", branch=branch)
    db.session.add(run)
    db.session.commit()

    return f"""
    <p>CI Triggered for branch '{branch}' → Status {status}</p>
    <pre>{text}</pre>
    <a href="/" style="display:inline-block;padding:8px 12px;background:#007bff;color:white;text-decoration:none;border-radius:4px;">⬅ Back to Dashboard</a>"""

@app.route("/trigger-cd", methods=["POST"])
@login_required
def trigger_cd():
    run_id = request.form.get("run_id")
    status, text = trigger_workflow("cd.yml", inputs={"run_id": run_id})
    # Save workflow run for current user
    from models import WorkflowRun, db
    run = WorkflowRun(user_id=current_user.id, workflow="cd", run_id=run_id)
    db.session.add(run)
    db.session.commit()
    return f"""
    <p>CD Triggered → Status {status}</p>
    <pre>{text}</pre>
    <a href="/" style="display:inline-block;padding:8px 12px;background:#007bff;color:white;text-decoration:none;border-radius:4px;">⬅ Back to Dashboard</a>"""

@app.route("/status/<workflow>")
@login_required
def workflow_status(workflow):
    user_runs = WorkflowRun.query.filter_by(user_id=current_user.id, workflow=workflow).order_by(WorkflowRun.timestamp.desc()).all()
    return render_template("status.html", workflow=workflow, runs=user_runs,  user=current_user)


if __name__ == "__main__":
    app.run(debug=True, port=5001)