# Validation pipeline

Status: **complete**.

Validation checks root boundaries, file existence, SHA-256, decoding,
dimensions, source/output identity, visual plausibility, deterministic seed,
profile hash, ground-truth reference, and metadata completeness. Blank and
near-blank synthetic pages are handled explicitly.

Reports are written externally as JSON, CSV, and Markdown. `--quarantine`
copies invalid assets into the external quarantine area; it does not delete or
overwrite the original. Visual difficulty is rule-based and named
`estimated_visual_difficulty`, never accuracy.

