# Rollback report

## Recovery anchors

- Source commits: recorded in `MERGE_PROVENANCE.md`.
- Destination base: `b6e548a853991b872d804f5e71238d17fa7103a7`.
- Immutable backup: `E:\clouda_merge_backups\20260723_133514Z`.
- Stable backup pointer: `E:\clouda_merge_backups\CURRENT_BACKUP.txt`.
- Mutable state: `E:\clouda_merged_state`.

## Procedure

1. Stop Streamlit, Uvicorn, RQ workers, and schedulers.
2. Preserve the current external state by copying it to a new timestamped
   recovery folder; never overwrite the existing snapshot.
3. Point deployment back to the previous known-good Git commit.
4. Restore `clouda.sqlite3` with SQLite backup/restore semantics into a new
   target path and confirm `PRAGMA integrity_check = ok`.
5. Verify the restored database SHA-256 and schema version.
6. Switch `CLOUDA_DATABASE_PATH` and `CLOUDA_STATE_HOME` only after smoke tests.
7. Keep `app.db` archived; do not merge it automatically.

Rollback is pointer-based and additive. It does not require modifying either
source repository or deleting migrated evidence.
