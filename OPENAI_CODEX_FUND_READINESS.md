# OpenAI Codex Fund Readiness

## Project Name

Clouda PDF

## Repository URL

https://github.com/sahrasayed3-crypto/OCR_PROJECT

## One-Line Summary

Open-source, model-agnostic PDF-to-DOCX tooling preparing for reliable Arabic OCR evaluation and integration.

## Problem Statement

Arabic researchers, publishers, and archives need editable DOCX output from digital and scanned PDFs without losing reading order, page provenance, RTL text, footnotes, or uncertainty around OCR quality.

## Why The Project Matters

Arabic OCR for historical and degraded documents remains difficult, especially when pages mix Arabic and English, contain footnotes or marginalia, or come from weak scans. Clouda PDF separates verified direct extraction from future OCR claims so the project can improve transparently.

## Open-Source Status

The repository is prepared as an open-source project under the existing `LICENSE`. It includes contribution, security, testing, roadmap, and data-license documentation.

## Current Technical Status

- Born-digital PDF text extraction works.
- DOCX export works for text-first output.
- Page states include `digital_text`, `blank_page`, `near_blank`, and `pending_ocr_model`.
- Scanned-page OCR is not yet implemented.
- A primary model candidate has been selected. Training has not started yet because dataset licensing and written-permission verification are still in progress.
- The engine interface is model-agnostic.

## Key Completed Components

- Streamlit UI entry point.
- Conversion service and metadata contract.
- Direct PDF text extraction engine.
- DOCX export.
- Deterministic fixtures and automated tests.
- Local storage safety improvements.

## Current Limitations

- The selected primary model candidate is not final until licensing, integration, training/adaptation, evaluation, and acceptance testing are complete.
- No scanned-page CER/WER is claimed.
- Layout-perfect reconstruction is not implemented.
- ROCm support is not validated.

## Planned Use Of Codex

- Improve tests, documentation, and release hygiene.
- Integrate the selected primary OCR candidate behind the engine interface after licensing and permission checks are complete.
- Review security, data licensing, and reproducibility.
- Assist with benchmark automation and failure analysis.

## Planned Use Of OpenAI API Credits

- Prototype document understanding and correction workflows.
- Explore OCR post-correction and evaluation helpers.
- Generate synthetic degradation metadata or test assistance where legally allowed.

## Expected Open-Source Benefit

The project can provide reproducible Arabic OCR evaluation infrastructure and a practical PDF-to-DOCX workflow for researchers and archives.

## Dataset Licensing Status

Only small deterministic fixtures should be committed. Future benchmark data requires documented permission, license status, manifests, and hashes.

## Security And Privacy Position

The repository must not include secrets, uploaded user PDFs, generated DOCX outputs, logs, databases, model weights, or private permission emails.

## Reproducibility Plan

Maintain deterministic fixtures, documented test commands, dataset manifests, environment notes, and versioned benchmark outputs.

## 3-6 Month Milestones

- Finalize consented evaluation set.
- Verify the selected primary model candidate's license and written data permissions.
- Benchmark the selected candidate against fallback baselines.
- Publish CER/WER with methodology.
- Improve DOCX handling for footnotes and mixed reading order.

## Requested Support

Codex usage credits and technical support for open-source engineering, evaluation automation, and documentation quality.

## Suggested Application Answers

Use the sections above as draft answers. Do not submit an application until the maintainer reviews the repository state, licensing notes, and final audit.
