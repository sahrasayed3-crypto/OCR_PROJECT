# Security report

## Passed controls

- Repository scan: 498 tracked files; zero credential-pattern findings, zero
  forbidden tracked files, zero forbidden source paths, and zero oversized
  tracked files.
- Upload reads are chunked and bounded; PDF byte and page limits are enforced.
- Archive extraction rejects traversal, links, excessive members, excessive
  expansion, and suspicious compression ratios.
- XML parsing uses `defusedxml`; Pillow decompression limits are configured.
- Worker API uses trusted-host and security-header middleware plus rotatable
  header-key authentication.
- Temporary upload cleanup has Windows-safe regression coverage.
- User-document training requires two independent consent gates; both default
  to false.

## Findings

### SEC-001 — High — production identity is deployment-owned

The application has worker-to-worker header authentication, but end-user
identity and authorization are not bound to an enterprise provider. Do not
expose the UI publicly until SSO/session authorization is integrated and
tested. Relevant surfaces: `app.py`, `pdfword/worker_api.py`.

### SEC-002 — Medium — perimeter controls require deployment configuration

TLS termination, rate limiting, proxy request-size enforcement, and final
allowed hosts are not self-provisioned by the Python application. Apply the
controls in `docs/DEPLOYMENT.md` and verify them in staging.

### SEC-003 — Medium — dataset/code license decisions remain open

The catalog gate prevents unapproved training use, but legal approval is still
required for non-approved records and Project B provenance. See
`MERGE_LICENSE_REPORT.md`.

No secrets or credentials were copied into the merged repository. This review
does not claim that arbitrary secret-like strings inside excluded source
artifacts were opened; they were deliberately not read.
