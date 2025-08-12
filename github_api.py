import requests
import time
import jwt
from config import GITHUB_TOKEN, GITHUB_APP_ID, GITHUB_PRIVATE_KEY, REPO_OWNER, REPO_NAME

BASE_URL = "https://api.github.com"

def get_installation_token():
    """Generate installation token if using GitHub App, else return personal token."""
    if not GITHUB_APP_ID or not GITHUB_PRIVATE_KEY:
        return GITHUB_TOKEN  # Fallback for local testing

    # 1. Create JWT for GitHub App
    payload = {
        "iat": int(time.time()) - 60,
        "exp": int(time.time()) + (10 * 60),
        "iss": GITHUB_APP_ID
    }
    encoded_jwt = jwt.encode(payload, GITHUB_PRIVATE_KEY, algorithm="RS256")

    # 2. Get installation ID
    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github+json"}
    resp = requests.get(f"{BASE_URL}/app/installations", headers=headers)
    resp.raise_for_status()
    installation_id = resp.json()[0]["id"]

    # 3. Create installation access token
    resp = requests.post(f"{BASE_URL}/app/installations/{installation_id}/access_tokens", headers=headers)
    resp.raise_for_status()
    return resp.json()["token"]

def trigger_workflow(workflow_file, ref="master", inputs=None):
    """Trigger a GitHub Actions workflow."""
    token = get_installation_token()
    url = f"{BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{workflow_file}/dispatches"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    payload = {"ref": ref}
    if inputs:
        payload["inputs"] = inputs
    resp = requests.post(url, headers=headers, json=payload)
    return resp.status_code, resp.text
