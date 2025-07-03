# quick-project

A lightweight, scriptable Python project scaffolding tool.

This tool bootstraps new Python projects with my preferred development stack, including:

- Virtual environment setup (`.venv`)
- Git repository initialization
- PostgreSQL backend support
- CLI structure (with `argparse`)
- Optional Flask-based web interface
- Ruff linting and dev dependencies
- Optional GitHub repo creation via `gh`

## Features

- Python project structure with `src/`, `cli/`, `tests/`, `db/`
- Auto-generates `.gitignore`, `README.md`, `pyproject.toml`, and requirements files
- Optional Flask web front-end (`webapp/`)
- Dev tooling: Ruff, Pytest
- GitHub integration: prompts to initialize and push
- Safety checks for existing files, clean git status, and auth status

## Usage

```bash
python quickproj.py /path/to/new-project
```

User is prompted to:

- Create the project directory (if needed)
- Include a web frontend
- Install GitHub CLI (`gh`) if not found
- Authenticate GitHub if needed
- Push the new repo to GitHub

## Requirements

- Python 3.11+
- Git
- (Optional) GitHub CLI (`gh`) and a GitHub account
- (Optional) Homebrew (macOS) or `apt`/`dnf` (Linux) to auto-install `gh`

## License

MIT
