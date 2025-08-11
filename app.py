# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User  # <-- The import is fixed here
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
db.init_app(app)

@app.route("/")
def home():
    if "user_id" in session:
        return f'<h1>Welcome, User ID: {session["user_id"]}!, email</h1><a href="/logout">Logout</a>'
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
    # Make sure you have a register.html template or just reuse login.html
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)