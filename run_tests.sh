#!/usr/bin/env bash
set -e

VENV="backend/.venv/bin/python"
if [ -x "$VENV" ]; then
  exec "$VENV" -m pytest "$@"
else
  echo "No virtualenv found at $VENV. Create one and install dependencies:" >&2
  echo "  cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt" >&2
  exec python3 -m pytest "$@"
fi
