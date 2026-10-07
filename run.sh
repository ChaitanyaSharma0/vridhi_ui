#!/usr/bin/env bash
# Start Vriddhi (server + website) on http://localhost:8770/
cd "$(dirname "$0")"
if [ -d ".venv" ]; then source .venv/bin/activate; fi
exec python3 work/api/server.py
