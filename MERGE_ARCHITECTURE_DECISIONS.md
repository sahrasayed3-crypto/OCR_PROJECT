# Architecture decisions

## ADR-001 — Project A is the base runtime

Project A already provides the operational Streamlit PDF-to-DOCX application,
schema-3 database, worker boundary, and production-oriented test suite. Its
behavior and entry point remain intact.

## ADR-002 — Project B becomes an isolated data subsystem

Project B's reusable code is namespaced under `clouda_data`; tests, configs,
tools, and documentation follow the same boundary. This avoids ambiguous
top-level modules and preserves provenance without rewriting the runtime.

## ADR-003 — Contracts are dependency-neutral

`clouda_contracts` owns versioned identities, observations, storage URIs,
evaluation policy, queue names, and adapters. Runtime, data, training, and
model packages depend on contracts rather than importing one another.

## ADR-004 — Mutable artifacts live outside Git

Databases, downloads, manifests, logs, conversions, weights, checkpoints, and
reports use `StorageRoots` under `CLOUDA_STATE_HOME`. Paths stored in manifests
are portable URIs, not source-machine absolute paths.

## ADR-005 — Database merge is conservative

Schema-3 `clouda.sqlite3` is authoritative. Schema-2 `app.db` remains a legacy
archive because automatic row reconciliation risks corrupting identity and
history.

## ADR-006 — Risky capabilities are explicit

Local OCR, training, user-document learning, and model registration are
disabled by default. License gates, consent gates, pinned model revisions,
bounded retries, and queue isolation must all pass before activation.

## ADR-007 — Integration is incremental and reversible

Each subsystem was committed separately. Source snapshots remain untouched,
external assets are checksum-verified copies, and rollback switches Git/state
pointers rather than deleting evidence.
