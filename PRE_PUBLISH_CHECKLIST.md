# Pre-Publish Checklist

Date: 2026-07-13

## Current verification

- Tests: 145 passed, 0 failed.
- Coverage: 81% overall `pdfword` coverage (`80.88%` measured).
- Ruff: passed on the full project.
- Black: passed on the full project.
- mypy: passed with `python -m mypy .`.
- compileall: passed.
- Demo: passed; generated `direct_pdf_text`, `pending_ocr_model`, and `blank_page` states.

## Security and repository hygiene

- The real `data/runtime-test/openrouter_api_key.txt` file was removed without printing its contents.
- `data/runtime-test/openrouter_api_key.example.txt` contains only `OPENROUTER_API_KEY_PLACEHOLDER`.
- `.env` is ignored; `.env.example` remains as a safe template.
- Poppler/runtime bundles are ignored and must not be staged.
- Local runtime data under `data/`, `conversions/`, `backups/`, and `logs/` must not be staged.
- Final Git status count: 189 non-clean paths: 118 additions, 6 deletions, and 65 untracked paths.
- Ignored/excluded status paths: 66 collapsed ignored paths from `git status --ignored --short`.

## Manual review before staging

- Review the full `git status --short` list and stage only intentional source, docs, tests, config, and small generated fixtures.
- Keep `tools/poppler/`, `poppler-26.02.0/`, `.venv311/`, `tools/python/`, runtime data, logs, and user PDFs out of Git.
- Confirm license, repository owner, security contact, and company/founder facts.
- Do not claim scanned OCR accuracy, CER/WER, CUDA, ROCm, or GPU validation until measured with real ground truth.
