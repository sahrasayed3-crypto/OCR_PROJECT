# Resume and recovery

Status: **complete for rendering and distortion runs**.

Each run has a deterministic ID, run manifest, page records, heartbeat/update
timestamps, atomic JSONL writes, and a completion marker. Final states are
`complete`, `manual_review`, `quarantined`, and `skipped`; resuming does not
regenerate them.

An explicit interruption hook is available for recovery testing. Partial files
use hidden temporary names and are never treated as complete. Duplicate IDs
and existing output collisions fail closed.

Resume with the exact original manifest, profile, seed, variant count, and page
limit plus `distort-resume`.

