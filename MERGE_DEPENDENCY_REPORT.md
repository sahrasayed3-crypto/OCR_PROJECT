# Dependency report

The project uses Python `>=3.11,<3.12`, a single `pyproject.toml`, and layered
requirements files. Core dependencies are Pillow, pypdf, pypdfium2,
python-docx, and requests. Optional groups isolate:

- server: FastAPI, Starlette, python-multipart, Streamlit, Uvicorn;
- worker: Redis and RQ;
- data: PyYAML, defusedxml, jsonschema;
- tests: pytest, pytest-cov, HTTPX, fakeredis, PyMuPDF, pdfplumber;
- development: Ruff, Black, mypy, build.

Project B's package name and console entry points were renamed into the unified
distribution (`clouda-pdf`, `clouda-data`, `clouda-training`). Imports were
rewritten according to `MERGE_FILE_MAP.json`, eliminating the former top-level
package collision. GPU/ROCm dependencies are intentionally placeholders until
a licensed OCR model and tested hardware target are selected. No lock file was
invented; CI tests the declared Python 3.11 range on Windows and Linux.
