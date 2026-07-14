# Anthropic Support Readiness

## Project Summary

Clouda PDF is an open-source, model-agnostic PDF-to-DOCX project preparing for reliable Arabic OCR evaluation and integration. A primary model candidate has been selected, but training has not started yet.

## Why Claude / Claude Code Is Useful

Claude or Claude Code could help review Python code, improve documentation, design benchmark workflows, analyze OCR failure modes, and maintain release-readiness checklists.

## Planned Coding Tasks

- Add the selected primary OCR candidate behind the existing interface after licensing and permission gates are complete.
- Improve DOCX handling for footnotes, margins, and mixed reading order.
- Strengthen tests for corrupt PDFs, page ranges, storage cleanup, and low-memory behavior.

## Planned Documentation Tasks

- Maintain honest README status.
- Document dataset licensing and model evaluation.
- Prepare reproducible benchmark reports.

## Planned Testing Tasks

- CER/WER evaluation.
- Runtime and memory benchmarks.
- Arabic, English, mixed, blank, near-blank, old, degraded, and scanned-page fixtures.

## Expected API Usage

Potential use for code review, OCR post-correction experiments, benchmark analysis, and documentation drafting after privacy and data-licensing review.

## Open-Source Benefit

The project can help Arabic document digitization by publishing reproducible workflows and transparent model comparisons.

## Current Project Status

Direct PDF text extraction and DOCX export are implemented. A primary model candidate has been selected. Training has not started yet because dataset licensing and written-permission verification are still in progress, and scanned-page OCR is not yet implemented.

## Dataset Licensing Status

Future datasets require explicit source, permission, license, split, and hash metadata before use.

## Independent-Developer Status

Prepared as an independent open-source project. Final applications or contact forms should be reviewed and submitted manually by the maintainer.

## Requested Support

Developer or open-source support for code review, documentation, testing, and responsible OCR evaluation.
