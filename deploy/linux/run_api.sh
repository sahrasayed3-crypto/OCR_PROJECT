#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="${CLOUDA_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
API_PORT="${CLOUDA_API_PORT:-8000}"
cd "${PROJECT_DIR}"
exec "${PROJECT_DIR}/.venv/bin/python" -m uvicorn pdfword.worker_api:app \
  --host=0.0.0.0 --port="${API_PORT}" --workers=1
