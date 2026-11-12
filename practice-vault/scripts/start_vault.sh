#!/usr/bin/env bash
# ==============================================================================
# Sovereign Practice Vault - Process Runner & Service Watchdog
# Purpose: Boots the Uvicorn web server and Ollama backend in production.
# Invariants: Binds exclusively to loopback or designated local interface.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="${VAULT_ROOT}/venv/bin/python"

echo ">>> Starting Heath & City Practice Vault..."

# Optional fallback: Ollama service daemon (disabled by default).
# To activate Ollama as a secondary standby, export START_OLLAMA_FALLBACK=1.
if [[ "${START_OLLAMA_FALLBACK:-0}" == "1" ]]; then
  if ! curl -s http://127.0.0.1:11434 &>/dev/null; then
    echo ">>> Starting Ollama service daemon..."
    sudo systemctl start ollama || ollama serve &
    sleep 2
  fi
fi

cd "${VAULT_ROOT}/backend"
exec "${VENV_PYTHON}" main.py
