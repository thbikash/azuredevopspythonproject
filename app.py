from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, Task
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
db.init_app(app)

@app.route("/")
def home():
    if "user_id" in session:
        tasks = Task.query.filter_by(user_id=session["user_id"]).all()
        return render_template("tasks.html", tasks=tasks)
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect("/")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("login.html")

@app.route("/add", methods=["POST"])
def add_task():
    if "user_id" in session:
        title = request.form["title"]
        new_task = Task(title=title, user_id=session["user_id"])
        db.session.add(new_task)
        db.session.commit()
    return redirect("/")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=8000)

