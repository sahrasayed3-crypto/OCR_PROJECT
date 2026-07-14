# Model Selection Status

## Current Status

A primary model candidate has been selected. Training has not started yet because dataset licensing and written-permission verification are still in progress.

The selected candidate is not the final production OCR model yet. It must still pass license review, written data-permission checks, integration work, reproducible evaluation, and acceptance tests before any final OCR support claim is made.

The project currently supports direct text extraction from born-digital PDFs only. Scanned or image-only pages are marked as `pending_ocr_model`; they are not treated as successfully OCR-processed pages and they are not used to claim scanned-page OCR accuracy.

## Model-Agnostic Integration Point

Future OCR engines can be added through the generic `pdfword.engines.ExtractionEngine` interface and registered through `EngineRegistry`.

The current interface does not assume Tesseract, PaddleOCR, CUDA, ROCm, Hugging Face Transformers, a vision-language model, or any specific OCR architecture.

## AMD ROCm Status

Actual AMD/ROCm support will be proven only after the selected primary candidate is integrated and tested on documented AMD hardware and software versions.

Current ROCm-related tooling is diagnostic only. The project does not currently claim that OCR inference, training, fine-tuning, BF16, FP16, or GPU acceleration works on AMD.

## Accuracy Claims

There are currently no OCR accuracy claims for scanned pages.

Future accuracy reports must include CER, WER, Arabic old-script and modern-script results, medium and weak scan quality, mixed text, numbers, footnotes, speed, peak VRAM, and the tested hardware/software stack.
