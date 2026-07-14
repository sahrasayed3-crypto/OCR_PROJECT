# AMD ROCm Roadmap

## Current Status

ROCm support is not implemented and has not been tested.

The project is architecturally prepared for future AMD-compatible OCR integration through `pdfword.engines.ExtractionEngine`, but no trainable OCR model has been selected yet.

## Required Before Any ROCm Claim

1. Select an OCR model with documented AMD ROCm compatibility.
2. Add dependencies to `requirements-rocm.txt` with exact tested versions.
3. Add a system diagnostic report using `tools/system_rocm_info.py`.
4. Validate CPU fallback behavior.
5. Benchmark digital PDFs, scanned PDFs, Arabic, English, and mixed text.
6. Record CER/WER, throughput, memory, VRAM, driver, HIP, ROCm, and PyTorch versions.
7. Document unsupported GPUs and operating systems.

## Acceptance Criteria

- Tests pass without GPU.
- ROCm diagnostics correctly report unavailable ROCm without crashing.
- A scanned-page OCR model runs on AMD hardware.
- Accuracy and performance are reported honestly.
- README states the exact tested hardware and software stack.
