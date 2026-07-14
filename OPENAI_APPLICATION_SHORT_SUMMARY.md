# OpenAI Application Short Summary

Draft date: 2026-07-14

## 50-Word Version

Clouda PDF is an Apache-2.0, model-agnostic PDF-to-DOCX project for Arabic, English, and mixed-language documents. It currently supports born-digital PDF text extraction, DOCX export, page-state metadata, and OCR-readiness infrastructure. A primary model candidate is selected, but training awaits dataset licensing and written-permission verification.

## 100-Word Version

Clouda PDF is a public Apache-2.0 PDF-to-DOCX project focused on Arabic, English, and mixed-language documents. The current implementation extracts selectable text from born-digital PDFs, exports editable DOCX files, preserves page order and Arabic RTL handling, and marks scanned pages as `pending_ocr_model` instead of claiming unmeasured OCR success. The project includes tests, deterministic fixtures, model-agnostic engine interfaces, and evaluation planning. A primary model candidate has been selected, but it is not final. Training has not started because dataset licensing and written-permission verification are still in progress, and no final CER/WER results exist.

## 200-Word Version

Clouda PDF is a public Apache-2.0, model-agnostic PDF-to-DOCX project for Arabic, English, and mixed-language documents. It addresses a practical gap for researchers, publishers, archives, and digitization workflows that need editable documents while preserving page order, Arabic Unicode, RTL paragraph direction, footers, and page boundaries.

The current verified implementation supports born-digital PDF text extraction and text-first DOCX export. It classifies pages as `digital_text`, `blank_page`, `near_blank`, or `pending_ocr_model`, so scanned or image-only pages remain explicit review items rather than being treated as successful OCR. The repository includes a Streamlit entry point, conversion service, direct extraction engine, model-agnostic engine registry, metadata contract, deterministic tests, documentation, and evaluation planning.

A primary model candidate has been selected, but it is not the final production OCR model. Training has not started because dataset licensing and written-permission verification are still in progress. No scanned-page OCR, CER, or WER results are claimed. Codex API credits would support open-source maintenance, tests, documentation, release checks, security review, evaluation tooling, and approved future model integration after legal and evaluation gates are complete.

## One-Sentence Project Description

Clouda PDF is a public Apache-2.0, model-agnostic Arabic-focused PDF-to-DOCX project that currently supports verified born-digital text extraction and prepares a transparent path for future OCR evaluation.

## One-Sentence Credits Use

OpenAI API credits would support Codex-assisted tests, code review, maintainer automation, documentation consistency, release checks, security review, evaluation tooling, and approved future OCR integration.

## One-Sentence Licensing Status

Apache License 2.0 applies only to files actually present in the public repository; datasets, weights, adapters, checkpoints, private training recipes, production settings, permission correspondence, and brand assets remain outside the public license grant.

## One-Sentence Model Status

A primary model candidate has been selected, but training has not started because dataset licensing and written-permission verification are still in progress, and the candidate is not final until integration, evaluation, and acceptance tests are complete.
