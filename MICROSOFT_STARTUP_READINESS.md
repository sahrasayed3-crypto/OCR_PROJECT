# Microsoft For Startups / Azure Readiness

## Project Summary

Clouda PDF is an open-source PDF-to-DOCX project preparing for Arabic OCR evaluation with a model-agnostic architecture. A primary model candidate has been selected, but it is not final yet.

## Problem

Researchers and archives need reliable editable output from Arabic, English, and mixed PDFs, including historical or low-quality scans, without unsupported OCR claims.

## Solution

The current system provides verified direct PDF text extraction and DOCX export, with scanned pages routed to an explicit `pending_ocr_model` state until the selected primary model candidate is licensed, integrated, trained or adapted as needed, and measured.

## Target Users

Arabic researchers, publishers, libraries, archives, digitization teams, and developers working on document conversion.

## Current Status

Local development project with passing automated tests, a selected primary model candidate, no OCR training started yet, and no production cloud deployment.

## Open-Source Status

Prepared under the repository license with contribution, security, testing, roadmap, data-license, and third-party notices.

## Technical Architecture

Streamlit UI, conversion service, storage helpers, model-agnostic extraction engine interface, direct PDF text engine, DOCX export, and test fixtures.

## Proposed Azure Architecture

Future Azure usage could include Blob Storage for licensed datasets, Azure Machine Learning or GPU VMs for benchmarking the selected primary model candidate, and GitHub Actions for CI. No Azure resource should be created until reviewed manually.

## Security Plan

Do not commit secrets, `.env`, user PDFs, generated DOCX files, logs, databases, backups, model weights, or private permission evidence.

## Data Governance

Use only licensed or permissioned data. Track manifests, hashes, source, permission status, and split assignment.

## Expected Monthly Cloud Usage

Unknown. Initial usage should be limited to small benchmark runs after licensing is confirmed.

## Requested Credits / Support

Azure credits for controlled OCR benchmarking, optional GPU evaluation, storage of licensed datasets, and CI/CD hardening.

## 3-6 Month Roadmap

- Finalize licensed evaluation data and written permissions.
- Benchmark the selected primary OCR candidate against baselines.
- Integrate the candidate only after license and evaluation gates pass.
- Publish reproducible accuracy and performance reports.
- Improve DOCX output for footnotes and mixed reading order.

## Suggested Application Answers

Use this file as draft material only. Do not submit forms or activate Azure resources automatically.
