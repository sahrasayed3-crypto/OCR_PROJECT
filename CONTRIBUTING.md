# Contributing

Thank you for contributing to Clouda PDF.

## Development Setup

```powershell
py -3.11 -m venv .venv311
.\.venv311\Scripts\python.exe -m pip install --upgrade pip
.\.venv311\Scripts\python.exe -m pip install -r requirements-dev.txt
```

## Rules

- Do not commit secrets or runtime data.
- Do not add an OCR model without benchmark evidence and documentation.
- Do not claim AMD ROCm support before it is tested.
- Keep scanned-page OCR behind the generic engine interface until a model is selected.
- Run tests before submitting changes.

## Test Command

```powershell
.\.venv311\Scripts\python.exe -m pytest
```
