from dashboard import app
from models import db, User, Project

# --- Ensure app context is active ---
with app.app_context():
    # Create tables if they don't exist
    db.create_all()

    # Create a test user if none exists
    test_email = "test@example.com"
    user = User.query.filter_by(email=test_email).first()
    if not user:
        print(f"User '{test_email}' not found. Creating a minimal user...")
        user = User(email=test_email)
        user.set_password("changeme123")
        db.session.add(user)
        db.session.commit()
        print("User created with temporary password 'changeme123'.")

    # Seed projects
    projects = [
        {
            "name": "flask-sample-app",
            "repo_owner": "thbikash",
            "repo_name": "flask-sample-app",
            "default_branch": "main",
            "workflow_file": "ci.yml",
            "user_id": user.id
        },
        {
            "name": "node-sample-app",
            "repo_owner": "thbikash",
            "repo_name": "node-sample-app",
            "default_branch": "main",
            "workflow_file": "ci.yml",
            "user_id": user.id
        }
    ]

    for proj_data in projects:
        if not Project.query.filter_by(repo_name=proj_data["repo_name"]).first():
            proj = Project(**proj_data)
            db.session.add(proj)

    db.session.commit()
    print(f"Seeding complete. Created {len(projects)} project(s).")
