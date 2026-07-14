# Roadmap

This roadmap describes planned work only. It is not a claim that OCR, GPU acceleration, ROCm support, or accuracy benchmarks already exist.

## Current Status

- Born-digital PDF text extraction is implemented and tested.
- DOCX export preserves page order, Arabic Unicode, RTL paragraph direction, footers, and page boundaries.
- Image-only or scanned pages are detected and marked `pending_ocr_model`.
- No final OCR model has been selected, trained, integrated, or benchmarked.
- AMD ROCm readiness is architectural and diagnostic only.

## 0-2 Months

- Maintain the direct-text extraction path and metadata contract.
- Keep public fixtures deterministic, copyright-free, and small enough for Git.
- Build a consented ground-truth evaluation set for Arabic, English, mixed, old, degraded, blank, and near-blank pages.
- Define CER, WER, reading-order, footnote, layout, runtime, and memory evaluation methodology.
- Keep all OCR candidates behind the model-agnostic engine interface.

## 2-4 Months

- Evaluate legally usable OCR candidates such as Tesseract Arabic, PaddleOCR Arabic, Kraken/OpenITI-style Arabic models, Qwen-based approaches, QARI, AtlasOCR, Baseer, and any additional model with clear license status.
- Compare candidates on the same dataset, preprocessing, normalization rules, and hardware notes.
- Document unsupported cases and failure modes before integration.
- Validate optional CPU and AMD-compatible deployment paths if suitable hardware is available.

## 4-6 Months

- Integrate only the selected OCR engine as an optional dependency.
- Publish reproducible benchmark results with dataset scope, hardware, software versions, CER/WER, throughput, memory, and VRAM.
- Improve DOCX structure for footnotes, margins, tables, and reading order while preserving provenance and manual-review states.
- Prepare public release notes and support-program application materials from measured facts only.
