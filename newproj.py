#!/usr/bin/env python3
import argparse
import os
import subprocess
import platform
import shutil
from pathlib import Path

BASE_DEPENDENCIES = ["psycopg2-binary"]
DEV_DEPENDENCIES = ["ruff", "pytest"]

def run(cmd, cwd=None):
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)

def safe_write_file(filepath: Path, content: str):
    if filepath.exists():
        overwrite = input(f"⚠️ File '{filepath}' exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != "y":
            print(f"Skipping '{filepath.name}'")
            return
    filepath.write_text(content)
    print(f"Created: {filepath}")

def create_project_structure(base_path: Path, name: str, include_web: bool):
    dirs = ["cli", "src", "tests", "db", "scripts"]
    if include_web:
        dirs += ["webapp", "webapp/templates"]

    for d in dirs:
        (base_path / d).mkdir(parents=True, exist_ok=True)

    safe_write_file(base_path / "README.md", f"# {name}\n\nProject generated with `newproj.py`.")
    safe_write_file(base_path / ".gitignore", ".venv/\n__pycache__/\n*.pyc\n.env\n")
    safe_write_file(base_path / "LICENSE", "MIT License\n")
    safe_write_file(base_path / "requirements.txt", "\n".join(BASE_DEPENDENCIES) + "\n")
    safe_write_file(base_path / "requirements-dev.txt", "\n".join(DEV_DEPENDENCIES) + "\n")

    pyproject = """
[tool.ruff]
line-length = 100
exclude = ["migrations", "tests/data"]
target-version = "py311"
"""
    safe_write_file(base_path / "pyproject.toml", pyproject.strip() + "\n")

    safe_write_file(base_path / "cli" / "main.py", """\
import argparse

def main():
    parser = argparse.ArgumentParser(description="CLI Entry Point")
    args = parser.parse_args()
    print("CLI is working!")

if __name__ == "__main__":
    main()
""")

    if include_web:
        safe_write_file(base_path / "webapp" / "app.py", """\
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", title="Welcome")

if __name__ == "__main__":
    app.run(debug=True)
""")
        safe_write_file(base_path / "webapp" / "templates" / "index.html", """\
<!doctype html>
<html>
<head><title>{{ title }}</title></head>
<body><h1>{{ title }}</h1></body>
</html>
""")

def create_venv_and_install(base_path: Path):
    run("python3 -m venv .venv", cwd=base_path)
    run("./.venv/bin/pip install --upgrade pip", cwd=base_path)
    run("./.venv/bin/pip install -r requirements.txt -r requirements-dev.txt", cwd=base_path)

def init_git_repo(base_path: Path):
    run("git init", cwd=base_path)
    run("git add .", cwd=base_path)
    try:
        run("git commit -m 'Initial project scaffold'", cwd=base_path)
    except subprocess.CalledProcessError:
        print("⚠️ Git commit failed — possibly because there's nothing new to commit.")

def push_to_github(base_path: Path, name: str):
    try:
        subprocess.run(["gh", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("❌ GitHub CLI (`gh`) is not installed or not in PATH.")
        return

    if not gh_authenticated():
        print("⚠️ GitHub CLI is not authenticated.")
        auth = input("Run `gh auth login` now? (y/N): ").strip().lower()
        if auth == "y":
            try:
                run("gh auth login")
            except subprocess.CalledProcessError:
                print("❌ Authentication failed or was cancelled.")
                return
            if not gh_authenticated():
                print("❌ Still not authenticated after `gh auth login`. Aborting GitHub push.")
                return
        else:
            print("❌ Skipping GitHub push due to lack of authentication.")
            return

    visibility = input("GitHub repo visibility? [public/private] (default: private): ").strip().lower()
    if visibility not in ("public", "private"):
        visibility = "private"
    run(f"gh repo create {name} --source=. --{visibility} --push", cwd=base_path)


# --- GitHub CLI helpers ---
def github_cli_installed():
    return shutil.which("gh") is not None

def gh_authenticated():
    result = subprocess.run("gh auth status", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

def install_github_cli():
    system = platform.system()

    if system == "Darwin":
        if shutil.which("brew") is None:
            print("❌ Homebrew is not installed. Cannot install GitHub CLI.")
            return False
        print("Installing GitHub CLI via Homebrew...")
        run("brew install gh")
    elif system == "Linux":
        if shutil.which("apt") is not None:
            print("Installing GitHub CLI via apt...")
            run("sudo apt update && sudo apt install -y gh")
        elif shutil.which("dnf") is not None:
            print("Installing GitHub CLI via dnf...")
            run("sudo dnf install -y gh")
        else:
            print("❌ Unsupported Linux package manager.")
            return False
    else:
        print("❌ GitHub CLI installation not supported on this OS.")
        return False

    return github_cli_installed()

def main():
    parser = argparse.ArgumentParser(description="Scaffold a new Python project.")
    parser.add_argument("path", help="Path to the new project directory")
    args = parser.parse_args()

    base_path = Path(args.path).expanduser().resolve()
    name = base_path.name

    if not base_path.exists():
        create = input(f"Directory '{base_path}' does not exist. Create it? (y/N): ").strip().lower()
        if create != "y":
            print("Aborting.")
            return
        base_path.mkdir(parents=True)

    include_web = input("Include web frontend? (y/N): ").strip().lower() == "y"

    create_project_structure(base_path, name, include_web)
    create_venv_and_install(base_path)
    init_git_repo(base_path)

    gh_ready = github_cli_installed()
    if not gh_ready:
        offer = input("GitHub CLI not found. Install it now? (y/N): ").strip().lower()
        if offer == "y":
            gh_ready = install_github_cli()

    if gh_ready:
        push = input("Push to GitHub? (y/N): ").strip().lower()
        if push == "y":
            push_to_github(base_path, name)

    print(f"✅ Project '{name}' created at {base_path}")

if __name__ == "__main__":
    main()