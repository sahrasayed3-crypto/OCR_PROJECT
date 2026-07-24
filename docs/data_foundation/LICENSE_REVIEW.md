# License Review

> Historical note: the first paragraph below described the initial foundation
> state. It was superseded on 2026-07-23 by `PROJECT_STATUS.md` and the RASAM
> batch reports, which record a controlled local download. The historical text
> is preserved for auditability; current permissions are enforced through
> `dataset_catalog`.

No external datasets, books, PDFs, OCR model weights, or source document collections were downloaded during foundation preparation.

Future ingestion must record `source_license` for every document and should quarantine files with unclear permissions until reviewed.

Dataset acquisition preparation added a conservative registry at `data/manifests/dataset_registry.json`.

Verified commercial-use candidates:

- RASAM Dataset: Apache-2.0, sample approved with citation/notice conditions.
- SARD: Apache-2.0, approved with synthetic-data conditions.
- craneset public sample: MIT, approved for public sample only.
- Humans in the Loop Arabic Documents OCR Dataset: CC0-1.0, access requires manual form approval.

Blocked categories:

- NonCommercial licenses.
- Unclear licenses.
- Paid/restricted licenses without explicit user approval.
- Already distorted/noisy full datasets for the clean-source acquisition stage.
