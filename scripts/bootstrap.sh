#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required but was not found in PATH." >&2
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment in .venv"
    python3 -m venv .venv
fi

VENV_PYTHON="$REPO_ROOT/.venv/bin/python"
if [ ! -x "$VENV_PYTHON" ]; then
    echo "Virtual environment is missing .venv/bin/python; recreating .venv"
    rm -rf .venv
    python3 -m venv .venv
fi

echo "Upgrading pip"
"$VENV_PYTHON" -m pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    echo "Installing requirements.txt"
    "$VENV_PYTHON" -m pip install -r requirements.txt
fi

if [ -f "requirements-dev.txt" ]; then
    echo "Installing requirements-dev.txt"
    "$VENV_PYTHON" -m pip install -r requirements-dev.txt
fi

echo "Running pip health check"
"$VENV_PYTHON" -m pip check

echo "Installing pre-commit hooks"
"$VENV_PYTHON" -m pre_commit install

echo "Bootstrap complete"
echo "Use this Python for commands: $VENV_PYTHON"
