from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class WorkflowRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workflow = db.Column(db.String(50), nullable=False)   # e.g., "ci" or "cd"
    branch = db.Column(db.String(50))                     # for CI
    run_id = db.Column(db.String(50))                     # for CD
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('runs', lazy=True))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    repo_owner = db.Column(db.String(150), nullable=False)
    repo_name = db.Column(db.String(150), nullable=False)
    default_branch = db.Column(db.String(150), default="main")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    workflow_file = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Project {self.name}>"


   