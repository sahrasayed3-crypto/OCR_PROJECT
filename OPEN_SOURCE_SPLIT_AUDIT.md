# Open Source Split Audit

Audit date: 2026-07-14

## Executive Summary

The repository can be shaped as a public open-source framework/prototype for OCR_PROJECT / Clouda PDF while keeping commercial value outside the public repository. The current tracked code mainly contains public-safe architecture, model-agnostic interfaces, direct PDF text extraction, page routing, DOCX export, tests, public fixtures, and documentation. Private model artifacts, training datasets, production credentials, and customer data were not found in tracked Git history by the scans run in this audit.

Apache License 2.0 was applied to the public repository files after user approval. No Git history rewrite, deletion, or private-file publication was performed.

## Public Files

Public-scope files include:

- `pdfword/` source files for the public prototype and model-agnostic interfaces.
- `tests/` and deterministic public fixtures.
- `samples/sample_*` and `samples/generated/*_ref.txt` public sample/reference files currently tracked.
- `README.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `NOTICE`, `ROADMAP.md`, `THIRD_PARTY_NOTICES.md`, `DATA_LICENSES.md`.
- `docs/ARCHITECTURE.md`, `docs/MODEL_INTEGRATION.md`, `docs/MODEL_SELECTION_STATUS.md`, `docs/ROADMAP.md`, `docs/TESTING.md`, `docs/AMD_ROCM_ROADMAP.md`.
- `.github/workflows/ci.yml`, dependency files, test scripts, and safe examples.

## Private Files Or Local Areas

Private or excluded areas include:

- `data/`
- `conversions/`
- `logs/`
- `outputs/`
- `backups/`
- `audit_backups/`
- `.venv311/`
- `poppler-26.02.0/`
- `tools/python/`
- `tools/poppler/`
- `_git_metadata_backup/`
- `docs/permissions/` until manually reviewed for personal data and permission evidence.
- Any future `datasets/`, `data_private/`, `private/`, `weights/`, `models/`, `checkpoints/`, `adapters/`, `lora_adapters/`, `qlora_adapters/`, training caches, experiment artifacts, and generated distorted datasets.

## Files Moved

None. No private components were moved or deleted during this audit.

## Files Excluded

`.gitignore` was expanded to exclude private data, credentials, model artifacts, adapters, experiment outputs, local databases, training caches, generated distorted datasets, and local editor metadata.

## License Status

Current public repository license: Apache License 2.0.

Apache License 2.0 applies only to files present in the public repository. Private datasets, weights, LoRA/QLoRA adapters, checkpoints, training recipes, production settings, `docs/permissions/`, and trademarks/brand assets remain outside the public license unless separately released in writing.

## Legal Risks

- Publishing datasets, scans, or reference texts without clear permission may create copyright or privacy risk.
- Permission emails may contain personal data and should not be made public without review.
- Model weights and adapters may carry third-party license restrictions.
- Open-source publication is usually not revocable for already released versions.

## Commercial Risks

- Publishing final weights, adapters, training recipes, final hyperparameters, or advanced distortion tooling may weaken the commercial moat.
- Production configs and hosted service code could expose architecture or operational secrets.
- Public code licenses do not automatically protect trademarks or brand identity.

## Git History Status

Scans were run over all Git revisions for suspicious filenames and major secret patterns. The history showed only expected public/example paths such as `.env.example`, `deploy/linux/clouda.env.example`, `openrouter_api_key.example.txt`, `pdfword/checkpoints.py`, and OpenRouter client/test code. No actual API key pattern, GitHub token, AWS key, or private-key header was found by the history scan.

Backup status:

- Git history bundle created at `F:\project_collected_private\backups\project_collected_git_all_20260714_160938.bundle`.
- SHA256: `9F7E5BB7EBA322912523A40B35CACA43750A57FC011C49121B26701378399225`.
- A physical directory backup was attempted but did not fully complete within the time limit because of local runtime and virtual-environment files. No move/delete/history rewrite was performed.

## Secret Status

Current and history regex scans found no real OpenAI-style key, GitHub token, AWS access key, or private-key header in the public source scope. Placeholder and variable-name references remain acceptable.

## Test Results

- `.\.venv311\Scripts\python.exe -m pytest tests -q --cov=pdfword --cov-report=term-missing`: PASS, `146 passed`, total coverage `81%`.
- `.\.venv311\Scripts\python.exe -m compileall -q app.py pdfword scripts tests ...`: PASS.
- `.\.venv311\Scripts\python.exe -m ruff check .`: PASS.
- `.\.venv311\Scripts\python.exe -m black --check .`: PASS.
- `.\.venv311\Scripts\python.exe -m mypy .`: PASS.

## Codex Open Source Fund Suitability

The public portion is suitable as an open-source prototype/framework candidate after user review, provided the repository remains honest that:

- final scanned-page OCR is not implemented,
- no final OCR model is included,
- no CER/WER claim is made for scanned pages,
- private datasets, weights, adapters, and commercial service components remain outside the public repository.

## Commercially Protected Components

Protected components should include final OCR model artifacts, LoRA/QLoRA adapters, private data, private reference texts, training recipes, advanced distortion pipelines, production infrastructure, credentials, customer data, and brand/trademark assets.

## Decisions Needed From User

- Whether to adopt DCO sign-off or a contributor license agreement before accepting external contributions.
- Whether any `docs/permissions/` material can be sanitized and published.
- Whether any current tracked readiness documents should be simplified before public release.

## Public Release Safety

The tracked public source scope appears safe for public release based on this audit, but the repository should not be made Public until the user reviews:

- `PUBLIC_PRIVATE_BOUNDARY.md`
- `LICENSE_RECOMMENDATION.md`
- `COMMERCIAL_COMPONENTS_POLICY.md`
- `OPEN_SOURCE_SPLIT_AUDIT.md`
- `README.md`
- `CONTRIBUTING.md`
- `.gitignore`

## Proposed Changes Requiring Approval

- Move private local folders to `F:\project_collected_private`.
- Rewrite Git history if a future deeper scan finds sensitive content.
- Publish or redact permission evidence.
