# Model Evaluation Plan

No model is selected or claimed as supported until it passes this plan with documented license status and reproducible results.

## Candidate Models

- QARI
- AtlasOCR
- Baseer
- Qwen base model
- Qwen after fine-tuning
- Kraken Arabic/OpenITI-style models
- PaddleOCR Arabic
- Tesseract Arabic
- Any additional legally usable model with documented license terms

## Fair Comparison Rules

- Use the same frozen test set for every candidate.
- Use the same page images and same page ranges.
- Apply the same text normalization policy before CER/WER calculation.
- Record preprocessing, runtime options, hardware, software versions, and memory limits.
- Do not compare a fine-tuned model against baselines on data leaked from training.

## Metrics

- CER
- WER
- reading-order accuracy
- footnote and margin handling
- layout-region accuracy when boxes are available
- runtime per page
- throughput
- peak RAM and VRAM
- unsupported features
- error and timeout rate

## Required Outputs

- Per-model result table.
- Failure-mode notes.
- License status and redistribution limits.
- Hardware and software environment.
- Dataset manifest and hashes.
- Recommendation for integration, rejection, or further testing.

## Current Status

The current repository supports direct embedded-text extraction only. Scanned-page OCR remains `pending_ocr_model`; no CER/WER result should be presented as a final OCR benchmark.
