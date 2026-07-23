# Local System Report

Generated during foundation preparation on 2026-07-22.

## Observed System

- Operating system: Microsoft Windows NT 10.0.19045.0 / Windows-10-10.0.19045-SP0.
- Windows version: 2009 from `Get-ComputerInfo`; detailed WMI fields were partially blocked.
- CPU model: Intel64 Family 6 Model 60 Stepping 3, GenuineIntel.
- Core count: unavailable because WMI/CIM access was denied.
- Thread/logical processor count: 4 from `[System.Environment]::ProcessorCount`.
- RAM: unavailable because WMI/CIM access was denied.
- Available disk space on `E:`: 141,117,534,208 bytes free of 183,352,946,688 bytes.
- GPU model: unavailable because video-controller WMI/CIM access was denied.
- GPU memory: unavailable because video-controller WMI/CIM access was denied.
- Python versions: Python 3.12.10 installed; project venv uses `.venv/Scripts/python.exe`.
- Git availability: Git for Windows installed under `C:\Users\احمد\AppData\Local\Programs\Git`.
- PowerShell version: 5.1.19041.6456.
- Docker availability: not detected on PATH.
- WSL availability: not detected on PATH.
- CUDA availability: not detected; `nvidia-smi` not available on PATH.
- ROCm availability: not detected.
- Existing OCR tools: Tesseract OCR 5.5.0.20241111 detected.
- Existing PDF tools: `pdftoppm` not detected on PATH.
- Existing image-processing tools: ImageMagick `magick` and Ghostscript `gs` not detected on PATH.
- Existing virtual environments: `.venv/` created for this project.

## Readiness

- CPU-only preparation is supported and validated.
- Local GPU processing cannot be confirmed yet.
- Local work should include schema validation, profile validation, manifest checks, synthetic tests, and small previews only.
- AWS may be useful later for large-scale GPU experiments, but no AWS resource has been created.

## Validation Commands

- `scripts/setup/validate_environment.py`: passed.
- `python -m unittest discover -s tests -t .`: passed, 21 tests.
- `python -m clouda_data.pipeline.cli validate-project`: passed.
- `python -m clouda_data.pipeline.cli inspect-config`: passed.
- `python -m clouda_data.pipeline.cli list-profiles`: passed, 16 profiles.
