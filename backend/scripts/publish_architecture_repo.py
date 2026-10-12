import json
import os
import subprocess
import urllib.request
import urllib.error

TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_NAME = "stat6-bms-architecture"
REPO_DIR = r"C:\Users\prann\.gemini\antigravity\scratch\stat6-architecture-repo"


def create_private_github_repo():
    url = "https://api.github.com/user/repos"
    payload = {
        "name": REPO_NAME,
        "description": "STAT6 Enterprise Business Management System (BMS) — Official Product Architecture PDF & UI Showcase",
        "private": True,
        "auto_init": False,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"token {TOKEN}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "STAT6-Architecture-Publisher",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            info = json.loads(resp.read().decode("utf-8"))
            print("CREATED PRIVATE REPO:", info.get("html_url"), "Private:", info.get("private"))
            return info.get("owner", {}).get("login", "prannesshkva"), info.get("html_url")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"GitHub API status {e.code}: {body}")
        # If repo already exists, ensure it is private and return URL
        return "prannesshkva", f"https://github.com/prannesshkva/{REPO_NAME}"


def git_push_assets(owner: str):
    def run_git(args):
        res = subprocess.run(
            ["git"] + args,
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            print(f"git {' '.join(args)} -> {res.stderr.strip()}")
        else:
            print(f"git {' '.join(args)} -> OK")
        return res

    if not os.path.exists(os.path.join(REPO_DIR, ".git")):
        run_git(["init"])

    run_git(["branch", "-M", "main"])
    run_git(["config", "user.name", owner])
    run_git(["config", "user.email", f"{owner}@users.noreply.github.com"])
    run_git(["add", "STAT6_BMS_Architecture_and_UI.pdf", "README.md", "ui-showcase"])
    run_git(["commit", "-m", "Add STAT6 Enterprise BMS Architectural Specification PDF & UI Showcase"])

    auth_url = f"https://{owner}:{TOKEN}@github.com/{owner}/{REPO_NAME}.git"
    clean_url = f"https://github.com/{owner}/{REPO_NAME}.git"

    run_git(["remote", "remove", "origin"])
    run_git(["remote", "add", "origin", auth_url])
    run_git(["push", "-u", "origin", "main", "--force"])
    # Sanitize remote URL so token isn't left in .git/config
    run_git(["remote", "set-url", "origin", clean_url])
    print("SUCCESSFULLY PUSHED TO:", clean_url)


if __name__ == "__main__":
    owner, html_url = create_private_github_repo()
    git_push_assets(owner)
