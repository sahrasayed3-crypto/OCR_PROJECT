# Staged Files Review

Date: 2026-07-13
Branch: `readiness-20260713`

## Summary

- Staged files: 132
- Added files: 132
- Modified files: 0
- Deleted files: 0
- Secret scan on staged files: passed
- Staged files larger than 5 MiB: none
- Blocked local/runtime paths in staging: none

## Added files

- `.env.example`
- `.github/workflows/ci.yml`
- `.gitignore`
- `.streamlit/config.toml`
- `CHANGELOG.md`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `LICENSE`
- `PRE_PUBLISH_CHECKLIST.md`
- `PROJECT_READINESS_REPORT.md`
- `README.md`
- `SECURITY.md`
- `STAGED_FILES_REVIEW.md`
- `app.py`
- `assets/styles.css`
- `deploy/linux/README.md`
- `deploy/linux/backup.sh`
- `deploy/linux/cleanup.sh`
- `deploy/linux/clouda-api.service`
- `deploy/linux/clouda-backup.service`
- `deploy/linux/clouda-backup.timer`
- `deploy/linux/clouda-cleanup.service`
- `deploy/linux/clouda-cleanup.timer`
- `deploy/linux/clouda.env.example`
- `deploy/linux/clouda.service`
- `deploy/linux/health_check.sh`
- `deploy/linux/install.sh`
- `deploy/linux/run.sh`
- `deploy/linux/run_api.sh`
- `deploy/linux/stop.sh`
- `docs/ARCHITECTURE.md`
- `docs/MICROSOFT_STARTUPS_APPLICATION.md`
- `docs/MODEL_EVALUATION_TEMPLATE.md`
- `docs/MODEL_INTEGRATION.md`
- `docs/MODEL_SELECTION_STATUS.md`
- `docs/ROADMAP.md`
- `docs/TESTING.md`
- `mypy.ini`
- `openrouter_api_key.example.txt`
- `pdfword/__init__.py`
- `pdfword/accuracy.py`
- `pdfword/ai_model_router.py`
- `pdfword/auto_eval.py`
- `pdfword/backup.py`
- `pdfword/checkpoints.py`
- `pdfword/cleanup.py`
- `pdfword/constants.py`
- `pdfword/conversion_service.py`
- `pdfword/correction_learning.py`
- `pdfword/corrections.py`
- `pdfword/database.py`
- `pdfword/document_analysis.py`
- `pdfword/docx_export.py`
- `pdfword/engines.py`
- `pdfword/health.py`
- `pdfword/intelligence.py`
- `pdfword/job_queue.py`
- `pdfword/key_store.py`
- `pdfword/limits.py`
- `pdfword/local_engines.py`
- `pdfword/model_registry.py`
- `pdfword/models.py`
- `pdfword/ocr_pipeline.py`
- `pdfword/openrouter_client.py`
- `pdfword/provider_client.py`
- `pdfword/provider_router.py`
- `pdfword/ranges.py`
- `pdfword/self_learning.py`
- `pdfword/settings.py`
- `pdfword/storage.py`
- `pdfword/styles.py`
- `pdfword/ui_components.py`
- `pdfword/ui_status.py`
- `pdfword/worker.py`
- `pdfword/worker_api.py`
- `pdfword/worker_client.py`
- `pdfword/worker_tasks.py`
- `pytest.ini`
- `requirements-base.txt`
- `requirements-dev.txt`
- `requirements-linux.txt`
- `requirements-server.txt`
- `requirements-worker.txt`
- `requirements.txt`
- `run_project_collected.bat`
- `run_server.ps1`
- `scripts/demo.py`
- `start_clouda_all.bat`
- `start_clouda_all.ps1`
- `stop_clouda_all.bat`
- `stop_clouda_all.ps1`
- `stop_server.ps1`
- `test_project_collected.bat`
- `tests/fixtures/blank.pdf`
- `tests/fixtures/corrupt.pdf`
- `tests/fixtures/digital_text.pdf`
- `tests/fixtures/empty.pdf`
- `tests/fixtures/generate_fixtures.py`
- `tests/fixtures/mixed.pdf`
- `tests/fixtures/near_blank_page_number.pdf`
- `tests/fixtures/near_blank_stamp.pdf`
- `tests/fixtures/not_a_pdf.txt`
- `tests/fixtures/scanned.pdf`
- `tests/test_accuracy.py`
- `tests/test_ai_model_router.py`
- `tests/test_arabic_fixtures.py`
- `tests/test_benchmark_categories.py`
- `tests/test_conversion_service_paths.py`
- `tests/test_correction_learning.py`
- `tests/test_distributed_worker.py`
- `tests/test_document_analysis.py`
- `tests/test_final_readiness.py`
- `tests/test_intelligence.py`
- `tests/test_model_agnostic_engines.py`
- `tests/test_openrouter_provider_clients.py`
- `tests/test_provider_router.py`
- `tests/test_quality_acceptance_policy.py`
- `tests/test_ranges.py`
- `tests/test_readiness_pipeline.py`
- `tests/test_router_safety.py`
- `tests/test_runtime_features.py`
- `tests/test_self_learning_deep.py`
- `tests/test_self_learning_runtime.py`
- `tests/test_settings_storage_worker.py`
- `tests/test_storage_streaming.py`
- `tests/test_ui_redesign.py`
- `tools/configure_single_machine_env.py`
- `tools/generate_test_pdfs.py`
- `tools/post_benchmark_autoreview.ps1`
- `tools/post_benchmark_autoreview.py`
- `tools/refresh_openrouter_models.py`
- `tools/run_full_benchmark.py`

## Modified files

None staged as modified. This branch has no committed base yet, so publishable project files are staged as additions.

## Deleted files

None staged as deletions.

Six deleted paths were reviewed:

- `AGENTS.md`: empty legacy index entry; not needed for public package.
- `DISTRIBUTED_DEPLOYMENT.md`: empty legacy index entry; replaced by current deployment docs.
- `README_PORTABLE.md`: empty legacy index entry; portable runtime is excluded.
- `pdfword/paddle_ocr.py`: empty legacy index entry; PaddleOCR is unsupported and intentionally not published.
- `tests/test_paddle_ocr.py`: empty legacy index entry; PaddleOCR tests are unsupported and intentionally not published.
- `tools/setup_tesseract_windows.ps1`: empty legacy index entry; Tesseract setup is unsupported and intentionally not published.

## Excluded files and reasons

- `tools/poppler/`, `poppler-26.02.0/`: bundled Poppler binaries; ignored and not staged.
- `.venv311/`, `tools/python/`: local Python runtimes; ignored and not staged.
- `data/`, `conversions/`, `logs/`, `backups/`: runtime/user/local state; ignored and not staged.
- `.vscode/`: local editor configuration; not staged.
- `samples/`: generated benchmark samples and PDFs; not needed for safe GitHub staging because test fixtures live under `tests/fixtures/`.
- `assets/web_window.png`, root screenshots, `ui-reference.png`: generated/reference images; not required by source or tests.
- `GITHUB_AMD_READINESS_REPORT.md`, `GITHUB_UPLOAD_REPORT.md`, `MODEL_AGNOSTIC_READINESS_REPORT.md`: legacy reports with stale verification context; kept out of staging.
- `docs/AMD_ROCM_ROADMAP.md`, `requirements-rocm.txt`, `tools/system_rocm_info.py`: ROCm planning/diagnostic material; excluded from this staging set to avoid implying ROCm implementation or validation.

## Secret scan

Passed on staged files. Patterns checked included OpenRouter-style keys, AWS access-key IDs, private-key headers, fixed personal Windows paths, and Codex workspace paths.

The staged `openrouter_api_key.example.txt` contains only:

```text
OPENROUTER_API_KEY_PLACEHOLDER
```

## Files larger than 5 MiB inside staging

None.

## Remaining risk

- Manual review is still required before commit because this is a large first public staging set.
- Generated benchmark samples remain unstaged; regenerate them locally only when running benchmark tooling.
- No commit or push was performed.
