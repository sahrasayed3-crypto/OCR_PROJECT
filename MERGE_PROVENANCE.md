# Merge provenance

- Snapshot time (UTC): `2026-07-23T13:35:14Z`
- Pre-merge audit: `E:\merge_analysis\MERGE_AUDIT.md`
- Project A: `E:\project_collected`, branch `main`, commit
  `b6e548a853991b872d804f5e71238d17fa7103a7`.
- Project B: `E:\new ocr project`, branch `master`, commit
  `e9a2112df5aa245ddefe2271a62d9c325c184c48`.
- Both commits matched the expected revisions. No Streamlit, Uvicorn, or RQ
  process was active at snapshot time.
- The source repositories were treated as read-only. Secret values were not
  opened or copied.
- Exact source inventories and SHA-256 evidence are in
  `MERGE_SOURCE_INVENTORY.json` and `MERGE_SOURCE_HASHES.json`.
- Recovery snapshot: `E:\clouda_merge_backups\20260723_133514Z`; the stable
  pointer is `E:\clouda_merge_backups\CURRENT_BACKUP.txt`.

