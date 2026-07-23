# Project Status

Current phase: first controlled RASAM real-data acquisition and ingestion batch complete.

Completed work:

- Created requested directory structure, Python package skeleton, configuration system, schemas, validators, manifest/status/checkpoint foundations, evaluation foundations, CLI commands, synthetic fixtures, local AWS templates, and documentation.
- Created distortion profile definitions and metadata-only distortion interfaces only; real distortion generation has not started.
- Added data-ingestion workflow for PDF, DOCX, clean page images, plain text, structured JSON ground truth, PAGE XML, and ALTO XML.
- Added checksum-based file registration, duplicate detection, source-document manifests, page manifests, dry-run ingestion, and copy-based ingestion.
- Added license-aware dataset registry, dataset source report, license matrix, download plan, safe sample downloader, and dataset acquisition CLI commands.
- Downloaded the tiny RASAM downloader-validation sample: 38,835 bytes.
- Built the first controlled RASAM batch workflow with Windows trusted-certificate HTTPS support, per-manuscript public-domain IIIF rights checks, PAGE XML/image alignment verification, rejections, batch manifests, and quality reports.
- Downloaded the first controlled RASAM batch from official RASAM GitHub and BULAC/BiNA IIIF endpoints.
- Verified and ingested valid RASAM first-batch pages through the copy-based ingestion workflow.

RASAM first controlled batch:

- Source preserved at `data/downloads/rasam_dataset/first_batch/`.
- Managed ingested copies are under `data/raw/pages/` and `data/raw/ground_truth/`; the PAGE XML files in `data/raw/ground_truth/` carry both exact text and layout annotations.
- Batch manifest: `data/manifests/rasam_first_batch_manifest.json`.
- Rejections: `data/manifests/rasam_first_batch_rejections.jsonl`.
- Report: `docs/RASAM_FIRST_BATCH_REPORT.md`.
- Downloaded size: 48,846,110 bytes.
- Extracted size: 48,846,110 bytes.
- Pages downloaded: 100.
- Valid pages ingested: 88.
- Rejected pages: 12, all rejected for `empty_ground_truth`.
- Ground-truth coverage: 88/100.
- Layout-annotation coverage: 100/100.
- License conclusion: RASAM repository PAGE XML/metadata are Apache-2.0; external BULAC/BiNA IIIF images were downloaded only where source metadata reports public-domain rights.

Current work:

- First controlled clean-data batch is acquired, validated, reported, and copied into the managed raw data area.

Remaining work:

- Manually inspect the ingested RASAM batch before any distortion preview.
- Decide whether to replace the 12 empty-ground-truth pages with additional RASAM pages in a future approved batch.
- Replace placeholder future implementations with real rendering, distortion, OCR evaluation, and AWS execution in later approved phases.
- Full dataset acquisition has not started.

Blocked items:

- Detailed RAM/GPU/WMI hardware inspection is still blocked by local Windows permission restrictions.
- Local GPU processing cannot be confirmed because `nvidia-smi` is not available on PATH.
- Sources with unclear, noncommercial, paid/restricted, form-required, or already-distorted full-data status are blocked from automatic download.

Test and verification results:

- `python -m unittest discover -s tests -t .` passed: 38 tests.
- `python -m clouda_data.pipeline.cli validate-project` passed.
- `python -m clouda_data.pipeline.cli plan-rasam-first-batch --pages 100 --max-bytes 1073741824` passed the pre-download gate.
- `python -m clouda_data.pipeline.cli download-rasam-first-batch --pages 100 --max-bytes 1073741824` downloaded and verified the controlled batch.
- `python -m clouda_data.pipeline.cli verify-rasam-first-batch` passed.
- `python -m clouda_data.pipeline.cli inspect-source` passed for first-batch images and PAGE XML.
- `python -m clouda_data.pipeline.cli validate-source data/downloads/rasam_dataset/first_batch/source_manifest.json` passed.
- `python -m clouda_data.pipeline.cli find-duplicates` passed after copy and reported `{}`.
- `python -m clouda_data.pipeline.cli ingest data/downloads/rasam_dataset/first_batch/source_manifest.json --dry-run` passed.
- `python -m clouda_data.pipeline.cli ingest data/downloads/rasam_dataset/first_batch/source_manifest.json` passed.

Environment status:

- Python 3.12.10 is installed.
- Virtual environment exists at `.venv/`.
- Lightweight dependencies are installed from `requirements-dev.txt`.
- Git for Windows is installed at `C:\Users\احمد\AppData\Local\Programs\Git\cmd\git.exe`.
- CPU-only preparation is supported.
- Tesseract OCR 5.5.0.20241111 is available.

Distortion status: not started.

Training status: not started.

AWS status: not used.

Next safe action:

- Manually inspect a few ingested RASAM images, PAGE XML files, and extracted text records from `data/raw/` and `data/manifests/page_manifest.json`; only after that should a tiny distortion preview be planned.
