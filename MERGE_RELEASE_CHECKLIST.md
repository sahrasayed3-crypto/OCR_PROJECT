# Release checklist

## Completed

- [x] Source commits and SHA-256 inventories recorded.
- [x] Source repositories left unmodified.
- [x] Online SQLite backups and integrity checks completed.
- [x] Data and manifests copied outside Git and checksum-verified.
- [x] Shared contracts and isolated subsystem boundaries implemented.
- [x] Local OCR, training, and model registry disabled by default.
- [x] 253 tests passed with 80.42% coverage; no skips.
- [x] Ruff, Black, mypy, compileall, demo, CLI, and repository scan passed.
- [x] Wheel and source distribution built.
- [x] Windows/Linux Python 3.11 CI matrix added.
- [x] Rollback and operational documentation added.

## Required before public production

- [ ] Close SEC-001 production identity/authorization.
- [ ] Close SEC-002 TLS, host, rate, and request-limit controls.
- [ ] Obtain license approval for Project B and all intended datasets.
- [ ] Select and license pinned OCR weights; rerun security/evaluation gates.
- [ ] Exercise backup restore and failover in staging.
- [ ] Run the full CI matrix from a clean checkout.
- [ ] Configure monitoring, alerting, Redis durability, and secret rotation.
