# Split and leakage policy

Status: **complete**.

Train/validation/test assignment hashes the deterministic seed with the source
document ID. All pages and clean/distorted variants of a document therefore
remain in one split. Exact image hashes are deduplicated before splitting.
Perceptual deduplication remains an injectable hook.

Exports report split counts, rejected duplicates, SHA-256, and any document
leakage. Any leakage makes the CLI fail. Benchmark document exclusions can be
provided repeatedly.

