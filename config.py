import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# GitHub settings
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # For now: personal PAT
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")  # For later: GitHub App ID
GITHUB_PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY")  # Later: GitHub App private key

# Repo details
REPO_OWNER = os.getenv("REPO_OWNER", "username")
REPO_NAME = os.getenv("REPO_NAME", "azuredevopspythonproject")
REF = os.getenv("REF", "master")