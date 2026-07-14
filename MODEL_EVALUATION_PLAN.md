# Model Evaluation Plan

A primary model candidate has been selected. Training has not started yet because dataset licensing and written-permission verification are still in progress. The candidate is not claimed as the final supported model until it passes this plan with documented license status and reproducible results.

## Candidate And Baselines

- Selected primary model candidate, before and after any approved training/adaptation.
- Legally usable baselines such as QARI, AtlasOCR, Baseer, Kraken Arabic/OpenITI-style models, PaddleOCR Arabic, Tesseract Arabic, or any additional model with documented license terms.

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

The current repository supports direct embedded-text extraction only. Scanned-page OCR remains `pending_ocr_model`; no CER/WER result should be presented as a final OCR benchmark until the selected primary candidate is licensed, trained/adapted if needed, integrated, and evaluated.
