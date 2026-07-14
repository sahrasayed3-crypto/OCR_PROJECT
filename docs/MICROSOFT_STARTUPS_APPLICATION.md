# Microsoft for Startups Founders Hub — Draft Answers

Use only facts verified by the founder before submitting. This draft intentionally contains no invented revenue, user, company-registration, GPU, or accuracy claims.

## Project name

Clouda PDF

## One-line description

A model-agnostic PDF-to-editable-DOCX workflow for Arabic, English, and mixed documents, with transparent routing of scanned pages pending a validated OCR model.

## Problem

Archives, researchers, publishers, and small teams need editable text from PDFs, including Arabic and mixed RTL/LTR documents, without silent loss of page context or unsupported accuracy claims.

## Solution

Clouda PDF extracts the embedded text layer from born-digital PDFs, creates editable DOCX output with RTL-aware text handling, and records page-level metadata. Image-only pages are explicitly held as `pending_ocr_model` until the selected primary model candidate is licensed, integrated, trained or adapted as needed, and evaluated.

## Target users

Researchers, archives, publishers, librarians, legal and administrative teams, and organizations working with Arabic or mixed-language PDF collections.

## Product stage

Pre-Seed, working prototype with direct-text PDF conversion, DOCX output, page-level status metadata, automated tests, and a model-agnostic OCR integration boundary.

## Current progress

The digital-text path, DOCX export, page classification, test fixtures, and Windows CI are implemented. The latest local readiness run completed 145 tests with 81% overall coverage. A primary model candidate has been selected, but training has not started yet because dataset licensing and written-permission verification are still in progress.

## Why Azure is needed

Azure could provide secure staging, controlled storage, CI/CD, observability, and a future reproducible evaluation environment as the product progresses from local prototype to a managed service.

## Why GPU is needed

The current product does not require a GPU. A GPU may be evaluated later only for a selected OCR model after licensing, benchmark, cost, and ground-truth requirements are met.

## Expected Azure usage

Initial usage would focus on application hosting, managed secrets, storage for user-authorized files, CI/CD, logging, and isolated evaluation environments. Future compute usage depends on the selected OCR engine and validated demand.

## Technical architecture

Python application with Streamlit UI, optional FastAPI worker endpoints, direct PDF text extraction, model-agnostic `ExtractionEngine`/`EngineRegistry`, DOCX export, local storage controls, and page-level metadata.

## Competitive advantage

The product prioritizes transparent processing states, Arabic/RTL-aware editable output, and a model-agnostic boundary that prevents vendor lock-in or unsupported OCR claims.

## Current limitations

Scanned-page OCR is not yet available. There are no published scanned-page CER/WER results because a real ground-truth evaluation has not yet been completed. Layout-perfect reconstruction is outside the current scope.

## Roadmap for the next 6 months

Build a consented evaluation dataset; evaluate OCR candidates; integrate an optional validated engine; publish reproducible quality and performance results; and expand managed deployment only after the direct-text foundation remains stable.

## Funding stage

Bootstrapped / Pre-Seed.

## Submission fields that require founder verification

- Current revenue: omit unless verified and appropriate to disclose.
- Current users: omit counts unless verified.
- Company registration status: state the actual legal status only; it was not provided in this repository.
