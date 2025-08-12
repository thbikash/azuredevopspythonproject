from flask import Flask, render_template, request
from github_api import trigger_workflow, get_workflow_runs


app = Flask(__name__, template_folder="dashboard_templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/trigger-ci", methods=["POST"])
def trigger_ci():
    status, text = trigger_workflow("ci.yml")
    return f"CI Triggered → Status {status}<br>{text}"

@app.route("/trigger-cd", methods=["POST"])
def trigger_cd():
    run_id = request.form.get("run_id")
    status, text = trigger_workflow("cd.yml", inputs={"run_id": run_id})
    return f"CD Triggered → Status {status}<br>{text}"

@app.route("/status/<workflow>")
def workflow_status(workflow):
    runs = get_workflow_runs(f"{workflow}.yml")
    return render_template("status.html", workflow=workflow, runs=runs)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
