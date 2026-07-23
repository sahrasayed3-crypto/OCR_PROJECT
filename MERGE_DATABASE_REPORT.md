# Database migration report

Read-only inventory found:

| Database | Schema | Integrity | Decision |
|---|---:|---|---|
| `clouda.sqlite3` | 3 | ok | authoritative |
| `app.db` | 2 | ok | legacy archive |

The authoritative database contains 77 attempts, 3 conversions, and 1 user.
The legacy database contains 6 conversions and 2 users. Both contain zero
active absolute-path values.

No row-level merge was attempted: identities overlap, schemas differ, and a
lossless semantic mapping cannot be proven from code alone. The SQLite online
backup of `clouda.sqlite3` was copied to
`E:\clouda_merged_state\runtime\databases\clouda.sqlite3`; integrity is `ok`,
schema is 3, and SHA-256 is
`EB4BF09CEBC72F5A86B1CE5EC3603EE4597A75892810E1B840C8CAFCE3D2B3C9`.
The legacy file remains in the immutable backup only.
