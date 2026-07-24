# Security policy

The merged repository is private and pre-production until authentication,
legal ownership, and deployment decisions are complete.

Never commit secrets, `.env`, databases, user documents, datasets, logs,
backups, model weights, or checkpoints. Use external storage roots and run:

```text
python -m tools.validation.repository_scan --root .
```

Uploads are bounded by byte and page limits. DOCX and backup archives are
checked for traversal, links, member count, expansion size, and compression
ratio. XML uses `defusedxml`; images have a pixel limit. The worker API requires
a header key, validates hosts, disables docs, and sets baseline security
headers. Configure request limits, rate limiting, TLS, and authentication at a
trusted reverse proxy in production.

User documents are never training data by default. A code-level consent
boundary requires both document-specific consent and an approved policy; no
current runtime path calls it to admit documents to training.

Redis must bind to a private network and accept only isolated workers.
`CLOUDA_WORKER_API_KEY_PREVIOUS` is a temporary rotation hook and must be
removed after cutover. Local OCR remains disabled unless explicitly configured
with an approved, pinned model.

Report vulnerabilities privately with the affected component, reproduction,
impact, and suggested mitigation. Rotate any exposed credential immediately.
See [threat model](docs/security/THREAT_MODEL.md) and
[data privacy](docs/security/DATA_PRIVACY.md).
