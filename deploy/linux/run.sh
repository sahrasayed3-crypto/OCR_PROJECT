#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="${CLOUDA_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
PORT="${CLOUDA_PORT:-8501}"
cd "${PROJECT_DIR}"
exec "${PROJECT_DIR}/.venv/bin/python" -m streamlit run app.py \
  --server.headless=true \
  --server.address=0.0.0.0 \
  --server.port="${PORT}" \
  --browser.gatherUsageStats=false
