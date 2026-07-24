# Final merge report

## Outcome

Project A remains the operational PDF-to-DOCX runtime. Project B was integrated
incrementally as the isolated `clouda_data` subsystem, with shared contracts,
training/model scaffolds, migration utilities, tests, documentation, and CI.
No source repository was modified, no user data was committed, no model was
trained, and no restricted dataset or model weight was added to Git.

The exact Project B copy/rename/import map is `MERGE_FILE_MAP.json`. The exact
allowlist exclusions are `MERGE_EXCLUSIONS.json`. All destination changes are
independently enumerable with:

```powershell
git diff --name-status b6e548a853991b872d804f5e71238d17fa7103a7..HEAD
```

## Architecture

- `app.py` and `pdfword/`: production runtime and authoritative database owner.
- `clouda_data/`: catalogs, acquisition, ingestion, validation, and evaluation.
- `clouda_contracts/`: versioned IDs, storage URIs, observations, metric policy,
  queue names, archive safety, and adapters.
- `clouda_training/`: disabled-by-default, license-gated planning scaffold only.
- `clouda_models/`: disabled registry scaffold; no weights are present.
- `tools/migration/`: repeatable manifest, asset, and database evidence tools.
- `E:\clouda_merged_state`: external mutable state and verified datasets.
- `E:\clouda_merge_backups\20260723_133514Z`: immutable recovery snapshot.

## Reconciliation

482 assets totaling 95,639,372 bytes were copied outside Git and verified by
SHA-256; 267 checksum duplications were retained and reported, not deleted.
The RASAM review found 100 source pages: 88 valid and 12 rejected. The manifest
migration verified 177 records and 43,970,899 declared bytes, leaving zero
active absolute paths. Dataset catalog status is 13 total: 3
`approved_with_conditions`, 2 `blocked`, 5 `pending`, and 3 `research_only`.

## Verification

The complete suite passed: 253 tests, 80.42% runtime coverage. Ruff, Black,
mypy (170 source files), compileall, both CLIs, the conversion demo, repository
security scan, wheel build, and source distribution build passed. There were
no skipped tests in the final suite.

## Database

`clouda.sqlite3` schema 3 is authoritative. Its online backup passed SQLite
integrity checking and was checksum-copied to the external runtime state.
`app.db` schema 2 is retained as a legacy archive. No automatic row merge was
performed because the two files contain overlapping identities and different
schema generations.

## Deviations and blockers

The implementation follows the audit recommendation of incremental integration.
Training remains intentionally disabled. Production identity/authentication,
TLS/reverse-proxy controls, rate limiting, final legal approval for pending or
blocked datasets, and selection/licensing of OCR model weights remain external
release decisions. These do not block local/private execution of the merged
runtime but block an internet-exposed production release.
