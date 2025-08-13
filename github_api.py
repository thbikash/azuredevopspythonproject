import requests
import time
import jwt
from functools import lru_cache
from config import GITHUB_TOKEN, GITHUB_APP_ID, GITHUB_PRIVATE_KEY, REPO_OWNER, REPO_NAME

BASE_URL = "https://api.github.com"

def get_installation_token():
    # Personal PAT fallback for local dev
    if not GITHUB_APP_ID or not GITHUB_PRIVATE_KEY:
        return GITHUB_TOKEN

    payload = {
        "iat": int(time.time()) - 60,
        "exp": int(time.time()) + (10 * 60),
        "iss": GITHUB_APP_ID
    }
    encoded_jwt = jwt.encode(payload, GITHUB_PRIVATE_KEY, algorithm="RS256")
    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github+json"}

    resp = requests.get(f"{BASE_URL}/app/installations", headers=headers)
    resp.raise_for_status()
    installation_id = resp.json()[0]["id"]

    resp = requests.post(f"{BASE_URL}/app/installations/{installation_id}/access_tokens", headers=headers)
    resp.raise_for_status()
    return resp.json()["token"]

@lru_cache(maxsize=1)
def get_default_branch():
    """Fetch the repo's default branch (no hard-coding). Cached for this process."""
    token = get_installation_token()
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    resp = requests.get(f"{BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}", headers=headers)
    resp.raise_for_status()
    return resp.json()["default_branch"]

def trigger_workflow(workflow_file, inputs=None, ref=None):
    """
    ref: branch that contains the workflow file (defaults to the repo's default branch).
    inputs: dict of workflow_dispatch inputs (e.g., {"branch": "feature/foo"})
    """
    token = get_installation_token()
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}

    if ref is None:
        ref = get_default_branch()  # <- dynamic, no hard-coding

    payload = {"ref": ref}
    if inputs:
        payload["inputs"] = inputs

    url = f"{BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{workflow_file}/dispatches"
    resp = requests.post(url, headers=headers, json=payload)
    return resp.status_code, resp.text

def get_workflow_runs(workflow_file, branch=None, per_page=10):
    token = get_installation_token()
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}

    if branch is None:
        branch = get_default_branch()

    params = {"branch": branch, "per_page": per_page, "page": 1}
    url = f"{BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{workflow_file}/runs"
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()["workflow_runs"]
