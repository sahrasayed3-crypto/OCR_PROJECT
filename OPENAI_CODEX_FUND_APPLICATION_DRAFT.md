# OpenAI Codex Open Source Fund Application Draft

Draft date: 2026-07-14

This file is a manual-review draft. Do not submit it automatically. The maintainer must verify personal details, OpenAI Organization ID, repository status, and any program-specific form wording before copying answers into the OpenAI form.

## 1. Project Name

Clouda PDF / OCR_PROJECT

## 2. Repository URL

https://github.com/sahrasayed3-crypto/OCR_PROJECT

## 3. Short Project Description

Clouda PDF is an Apache-2.0, model-agnostic PDF-to-DOCX project for Arabic, English, and mixed-language documents. The current public release supports verified born-digital PDF text extraction, DOCX export, page-state metadata, and OCR-readiness infrastructure while scanned-page OCR remains pending.

## 4. Detailed Project Description

Clouda PDF converts selectable-text PDFs into editable DOCX files while preserving page order, Arabic Unicode, RTL paragraph direction, footers, and page boundaries. It intentionally separates verified direct PDF text extraction from future OCR claims. Image-only or scanned pages are detected and routed to `pending_ocr_model` instead of being treated as successful OCR output.

The public repository contains a Streamlit entry point, conversion service, direct extraction engine, model-agnostic engine interface, page-state metadata contract, DOCX exporter, deterministic fixtures, tests, and documentation. It is designed so a future OCR model can be integrated behind a generic engine contract only after licensing, written data permissions, evaluation, and acceptance tests are complete.

## 5. The Problem The Project Solves

Arabic researchers, publishers, and archives often need editable Word documents from PDFs while preserving Arabic text direction, page provenance, and uncertainty around pages that require OCR. Many workflows silently mix successful extraction with unmeasured OCR guesses. Clouda PDF makes the verified path explicit and keeps uncertain scanned pages in a review state.

## 6. Why Arabic OCR Is Underserved

Arabic OCR is harder for historical and degraded documents because documents may include old typefaces, diacritics, mixed Arabic-English text, marginalia, footnotes, weak scans, page curvature, and inconsistent reading order. Useful open tooling also needs transparent licensing and evaluation practices so maintainers do not publish unverified accuracy claims or uncleared training data.

## 7. Current Technical Status

- Born-digital PDF text extraction is implemented and tested.
- Text-first DOCX export is implemented.
- Page states include `digital_text`, `blank_page`, `near_blank`, and `pending_ocr_model`.
- The OCR engine contract is model-agnostic.
- Scanned-page OCR is not implemented as a validated production feature.
- No final scanned-page CER or WER results exist.
- AMD/ROCm readiness is architectural and diagnostic only; no GPU inference or training is claimed.

## 8. Current Model-Candidate Status

A primary model candidate has been selected. Training has not started yet because dataset licensing and written-permission verification are still in progress.

The selected candidate is not the final production OCR model. It must still pass license review, written data-permission checks, integration work, reproducible evaluation, and acceptance tests before any final OCR support claim is made.

## 9. What Is Already Implemented

- Streamlit application entry point.
- Local conversion workflow.
- Direct PDF text extraction engine.
- DOCX export for editable text output.
- Page-state routing and JSON metadata.
- Blank-page and near-blank handling.
- Model-agnostic engine registry and interfaces.
- Deterministic test fixtures.
- Automated test suite and quality checks.
- Public documentation for architecture, licensing boundaries, evaluation planning, and model integration.

## 10. What Is Not Yet Implemented

- Validated scanned-page OCR.
- Final production OCR model integration.
- Training or fine-tuning of the selected candidate.
- Final CER/WER benchmarks.
- Public benchmark dataset release.
- Confirmed AMD/ROCm inference or training.
- Layout-perfect reconstruction of images, tables, margins, or page artwork.
- Public release of datasets, weights, LoRA/QLoRA adapters, checkpoints, or private training recipes.

## 11. How Codex API Credits Would Be Used

Credits would support open-source engineering tasks: adding and reviewing tests, improving documentation, maintaining release checklists, automating issue and pull-request triage, reviewing security-sensitive changes, improving evaluation scripts, generating reproducibility checks, and helping integrate an approved OCR candidate after licensing and permission gates are complete.

Credits would not be used to publish private datasets, expose permission correspondence, or build a closed commercial-only component.

## 12. Concrete Milestones

## First 30 Days

- Review and tighten public documentation and issue templates.
- Add maintainer automation for release checks, public/private boundary checks, and documentation consistency.
- Improve tests around page-state routing, DOCX output, and error handling.
- Finalize the dataset permission tracking format without exposing private correspondence.

## First 60 Days

- Complete written-permission and dataset-license verification for the first evaluation set.
- Build reproducible evaluation scripts for CER, WER, reading order, runtime, and failure-mode reporting.
- Add optional engine-integration scaffolding for the selected primary candidate without making it a required dependency.
- Expand CI checks for public fixtures and documentation claims.

## First 90 Days

- Evaluate the selected primary candidate and legally usable baselines on the same consented ground-truth set.
- Publish benchmark results only if licensing, methodology, and reproducibility requirements are satisfied.
- Integrate the approved OCR engine behind the model-agnostic interface if it passes acceptance gates.
- Prepare a public release note that clearly separates implemented features from future work.

## 13. Expected Open-Source Benefit

The project can give Arabic-document maintainers a transparent, reproducible PDF-to-DOCX foundation and an evaluation path for OCR without overstating unmeasured accuracy. The public code is useful even before private datasets or model weights are available because it supports direct extraction, document export, page-state metadata, tests, and extension points.

## 14. Who Will Use The Project

Potential users include Arabic researchers, small publishers, digitization volunteers, archives, libraries, educators, and developers building OCR workflows for Arabic, English, and mixed-language PDFs.

## 15. Why This Project Is A Strong Fit For Open-Source Support

The project is public, Apache-2.0 for repository files, and focused on a clear underserved document-processing problem. It is conservative about licensing and accuracy claims, and it can use Codex for the kind of maintainer work the program supports: code review, test generation, release workflows, documentation consistency, and security-aware automation.

## 16. Licensing Status

The public repository files are licensed under Apache License 2.0 unless a file states otherwise. Apache 2.0 applies only to files actually present in the public repository. It does not cover datasets, private reference texts, model weights, LoRA/QLoRA adapters, checkpoints, private training recipes, production configuration, permission correspondence, trademarks, logos, or brand assets.

## 17. Dataset-Permission Status

Dataset licensing and written-permission verification are still in progress. The public repository includes only deterministic fixtures, safe examples, and documentation. Private permission evidence, correspondence, datasets, and training materials are not included in the public repository.

## 18. Risks And Blockers

- Dataset licensing and written permissions must be completed before training starts.
- No final scanned-page OCR accuracy can be claimed until a consented evaluation set exists.
- The selected model candidate may fail license, integration, quality, or resource-usage gates.
- AMD/ROCm support must be validated on real documented hardware before any claim is made.
- Private data and permission correspondence must remain outside the public repository.

## 19. Requested Support Amount

Requested range: USD 10,000 to USD 20,000 in OpenAI API credits.

This range is intended for staged open-source engineering work over roughly 90 days: maintainer automation, test generation, security review, evaluation tooling, documentation review, and assisted integration after legal gates are satisfied. It is below the published maximum and should be adjusted by the maintainer based on actual expected usage and OpenAI program guidance.

## 20. Additional Information

Clouda PDF is intentionally careful about what it does and does not claim. The repository is already useful for born-digital PDF extraction and OCR-readiness work, while scanned-page OCR remains pending until data permissions, model licensing, integration, training or adaptation where needed, and reproducible evaluation are complete.

## Form-Size Drafts

## Why Does This Repository Qualify? (500 Characters Max)

Clouda PDF addresses Arabic PDF-to-DOCX and OCR-readiness, an underserved area for historical, degraded, and mixed Arabic-English documents. The public Apache-2.0 repository already provides direct PDF text extraction, DOCX export, page-state metadata, tests, and model-agnostic OCR integration scaffolding without overstating unverified OCR accuracy.

## How Will You Use API Credits? (500 Characters Max)

I would use credits for open-source maintenance: Codex-assisted tests, code review, release checks, documentation consistency, issue triage, evaluation tooling, and security review. Credits would also help integrate the selected OCR candidate only after dataset licensing and written permissions are verified. No private datasets or weights would be published.

## Anything Else We Should Know? (500 Characters Max)

A primary model candidate has been selected, but training has not started because dataset licensing and written-permission verification are still in progress. No final CER/WER or production scanned-page OCR claim is made. The public repository remains useful independently through direct extraction, DOCX export, metadata, tests, and evaluation scaffolding.
