# Data lifecycle

Status: **complete for preview, failed-output, temporary, and archive flows**.

Cleanup is dry-run by default and prints a target-specific confirmation token.
Execution moves files into recoverable external lifecycle trash; source data
and manifests are never deleted. Audit reports preserve original paths,
sizes, and SHA-256.

Run archives contain every asset plus `ARCHIVE_MANIFEST.v1.json`. Verification
checks safe ZIP structure and every member checksum. Existing archives are
never overwritten.

