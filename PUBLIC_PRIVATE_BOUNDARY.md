# Public / Private Boundary

## Purpose

This document defines the intended boundary between the public open-source repository and components that should remain private or separately licensed.

## Public Open-Source Components

| Component | Classification | Reason | Risk If Published |
| --- | --- | --- | --- |
| `README.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `ROADMAP.md`, public readiness docs | Public | Explains scope, safe usage, and project status | Low if it avoids unsupported claims |
| `pdfword/engines.py`, `pdfword/model_registry.py`, `pdfword/provider_router.py`, `pdfword/ocr_pipeline.py` | Public | Provides model-agnostic interfaces, routing, and extension points | Medium if future proprietary engine code is copied into these files |
| Page routing, blank-page and near-blank handling, metadata schemas | Public | Useful framework behavior and prototype value | Low to medium; avoid embedding private tuning heuristics |
| `pdfword/accuracy.py`, `pdfword/auto_eval.py`, public benchmark utilities | Public | General evaluation infrastructure | Medium if private benchmark data or final scoring thresholds are added |
| `tests/`, `tests/fixtures/`, safe generated sample references | Public | Verifies the public prototype | Low if fixtures remain synthetic or copyright-free |
| `scripts/demo.py`, public setup scripts, `.env.example`, deploy examples | Public | Safe local demonstration and reproducible setup | Medium if production credentials or private infrastructure details are added |
| `.github/workflows/ci.yml` | Public | Runs public tests and checks | Low if no secrets or paid GPU jobs are added |

## Private / Non-Published Components

| Component | Classification | Reason | Risk If Published |
| --- | --- | --- | --- |
| Training datasets and private reference texts | Private | May contain licensed, permissioned, or commercially valuable data | Legal exposure, data leakage, loss of competitive advantage |
| Final OCR model weights | Private / separately licensed | Core commercial value and possible third-party license constraints | Loss of exclusive value and redistribution violations |
| LoRA / QLoRA adapters and checkpoints | Private / separately licensed | Can reveal training work and model capabilities | Commercial leakage and possible license conflicts |
| Exact training recipe, final hyperparameters, advanced distortion pipeline | Private | Represents optimization knowledge and competitive edge | Competitors can reproduce the proprietary model |
| Private data-collection tools | Private | May encode source access, permissions, or workflow secrets | Legal/commercial leakage |
| API keys, `.env`, credentials, production cloud configs | Private | Operational secrets | Account compromise and cloud cost risk |
| Customer data, uploaded PDFs, generated DOCX output, logs, databases | Private | User or business data | Privacy and compliance risk |
| `docs/permissions/` local files | Private until reviewed | May contain permission contacts or email-derived evidence | Personal data and private correspondence exposure |
| `data/`, `conversions/`, `logs/`, `outputs/`, `backups/`, `audit_backups/` | Private local runtime data | Generated or local working state | Accidental publication of user files or operational details |
| Local bundles such as `.venv311/`, `poppler-26.02.0/`, `tools/python/`, `tools/poppler/` | Private local tooling | Large third-party/runtime bundles not suitable for Git | Repository bloat and license packaging risk |

## Relationship Between Public And Private Parts

The public repository should work as a prototype and framework. It can validate digital PDF extraction, DOCX export, page-state routing, interfaces, tests, and public evaluation scaffolding without exposing private models or data.

The complete commercial system may require separately licensed data, trained model weights, proprietary adapters, production infrastructure, and private service logic. Those components should stay outside the public repository unless the owner explicitly approves a separate release.

## Running The Public Prototype

Users can run the current public prototype with the documented Python dependencies and public fixtures. The prototype supports born-digital PDF extraction and routes scanned pages to `pending_ocr_model`.

## Running The Full System

The full system would require components that are not included here: final OCR model artifacts, licensed training/evaluation data, production configuration, credentials, and any private commercial service layer.

## Decision Status

No files were moved or deleted during this audit. Private local directories remain on disk and are excluded from Git by policy.
