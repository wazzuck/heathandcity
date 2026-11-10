#!/usr/bin/env bash
# ==============================================================================
# Sovereign Practice Vault - Host Machine Setup Script for Lenovo ThinkCentre
# Target OS: Ubuntu 24.04 LTS / Debian 12 (Headless)
# Language: British Professional English
# ==============================================================================

set -euo pipefail

echo ">>> [1/5] Verifying CPU AVX2 instruction support..."
if grep -q "avx2" /proc/cpuinfo; then
  echo "    CPU AVX2 vector instructions verified."
else
  echo "    WARNING: AVX2 instructions not detected; model inference may degrade."
fi

echo ">>> [2/5] Installing core host packages and OCR utilities..."
sudo apt-get update -y
sudo apt-get install -y \
  python3-pip python3-venv \
  tesseract-ocr tesseract-ocr-eng \
  cifs-utils poppler-utils curl git

echo ">>> [3/5] Verifying Ollama inference runtime..."
if ! command -v ollama &>/dev/null; then
  echo "    Installing Ollama engine..."
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "    Ollama engine already installed."
fi

echo ">>> [4/5] Pulling Small Language Model (SLM) weights..."
ollama pull nomic-embed-text
ollama pull llama3.2:3b

echo ">>> [5/5] Initialising Python virtual environment and dependencies..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(dirname "$SCRIPT_DIR")"

python3 -m venv "${VAULT_ROOT}/venv"
source "${VAULT_ROOT}/venv/bin/activate"
pip install --upgrade pip
pip install -r "${VAULT_ROOT}/backend/requirements.txt"

echo ">>> Setup completed successfully."
