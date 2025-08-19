from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User , WorkflowRun, Project
from github_api import trigger_workflow, get_workflow_runs,get_user_repos
import requests

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

@app.context_processor
def utility_processor():
    # Makes get_workflow_runs available in all templates
    return dict(get_workflow_runs=get_workflow_runs)

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

        # --- Seed default projects for this user ---
        default_projects = [
            {
                "name": "flask-sample-app",
                "repo_owner": "thbikash",
                "repo_name": "flask-sample-app",
                "default_branch": "main",
                "workflow_file": "ci.yml",
            },
            {
                "name": "node-sample-app",
                "repo_owner": "thbikash",
                "repo_name": "node-sample-app",
                "default_branch": "main",
                "workflow_file": "ci.yml",
            }
        ]
        for p in default_projects:
            proj = Project(user_id=user.id, **p)
            db.session.add(proj)
        db.session.commit()
        # --- End seeding ---

        return "<p>Registration successful! Two default projects created.</p><a href='/login'>Go to Login</a>"

    return render_template("register.html")


@app.route("/")
@login_required
def index():
    repos = get_user_repos(owner="thbikash")
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "index.html",
        user=current_user,
        repos=repos,
        projects=projects
    )

@app.route("/trigger-ci", methods=["POST"])
@login_required
def trigger_ci():
    repo_name = request.form.get("repo_name")
    branch = request.form.get("branch") or "main"

    status, text = trigger_workflow(
        "ci.yml",
        owner="thbikash",  # or dynamic from repo data
        repo=repo_name,
        inputs={"branch": branch}
    )
    return f"<p>CI Triggered for {repo_name} on branch {branch}</p><pre>{text}</pre>"


@app.route("/trigger-cd", methods=["POST"])
@login_required
def trigger_cd():
    # Get the combined run ID, owner, and repo from the form
    form_data = request.form.get("run_id")
    
    # NEW: Get the selected deployment target from the form
    deployment_target = request.form.get("deployment_target")

    try:
        run_id, owner, repo = form_data.split('|')
    except (ValueError, TypeError):
        return "Invalid CD trigger data received from form.", 400

    # NEW: Add the deployment_target to the inputs payload for the workflow
    workflow_inputs = {
        "run_id": run_id,
        "target": deployment_target
    }

    status, text = trigger_workflow(
        "cd.yml", 
        owner=owner, 
        repo=repo, 
        inputs=workflow_inputs
    )
    
    # Save workflow run for current user
    from models import WorkflowRun, db
    run = WorkflowRun(user_id=current_user.id, workflow="cd", run_id=run_id)
    db.session.add(run)
    db.session.commit()
    return f"""
    <p>CD Triggered for {owner}/{repo} to target '{deployment_target}' → Status {status}</p>
    <pre>{text}</pre>
    <a href="/" style="display:inline-block;padding:8px 12px;background:#007bff;color:white;text-decoration:none;border-radius:4px;">⬅ Back to Dashboard</a>"""

@app.route("/status/<workflow>")
@login_required
def workflow_status(workflow):
    user_runs = WorkflowRun.query.filter_by(user_id=current_user.id, workflow=workflow).order_by(WorkflowRun.timestamp.desc()).all()
    return render_template("status.html", workflow=workflow, runs=user_runs,  user=current_user)

@app.route("/project/<int:project_id>/builds")
@login_required
def project_builds(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()

    # fetch workflow runs from GitHub
    runs = get_workflow_runs(
        workflow_file="ci.yml",
        owner=project.repo_owner,
        repo=project.repo_name
    )

    return render_template(
        "builds.html",
        user=current_user,
        project=project,
        runs=runs
    )


@app.route("/projects/<int:project_id>/runs")
@login_required
def view_runs(project_id):
    project = Project.query.get_or_404(project_id)

    # GitHub Actions API endpoint for workflow runs
    url = (
        f"https://api.github.com/repos/"
        f"{project.repo_owner}/{project.repo_name}/actions/runs"
    )

    # No authentication - public repo only
    headers = {"Accept": "application/vnd.github+json"}

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return f"Error fetching runs: {r.status_code} - {r.text}", 500

    data = r.json()
    workflow_runs = data.get("workflow_runs", [])

    return render_template(
        "status.html",
        project=project,
        runs=workflow_runs
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
