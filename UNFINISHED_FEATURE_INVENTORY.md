# Unfinished feature inventory

Generated from a context-aware repository scan on 2026-07-23. Exception
classes, protocol ellipses, test mocks, UI placeholders, and deliberate
best-effort cleanup `pass` statements are not defects.

| ID | File / symbol | Current behavior | Intended behavior | Priority | Classification | Dependencies / risk / test |
|---|---|---|---|---|---|---|
| UF-001 | `clouda_data/rendering/interfaces.py` | Data contracts only | Bounded PDF/image renderer with manifests and resume | critical | implement now | Pillow, pypdfium2; decompression/path risk; rendering integration tests |
| UF-002 | `clouda_data/distortion/base.py:MetadataOnlyDistortion` | Returns unchanged pixels | Keep only as explicit test operator | critical | implement now | Preserve compatibility; pixel-change test |
| UF-003 | `clouda_data/distortion/registry.py:default_registry` | Registers every operator as metadata-only | Register real deterministic operators | critical | implement now | Pillow; deterministic and decode tests |
| UF-004 | `clouda_data/distortion/pipeline.py` | Metadata replay only | Real ordered/probabilistic pixel pipeline | critical | implement now | Ordering, budget, compatibility tests |
| UF-005 | `clouda_data/pipeline/cli.py` reserved handlers | Render/distort/validate/evaluate/resume return status 2 | Safe operational CLI | critical | implement now | CLI integration and root-boundary tests |
| UF-006 | distortion JSON profiles | Legacy metadata profiles | Versioned validated YAML production profiles | high | implement now | PyYAML/jsonschema; schema tests |
| UF-007 | manifests/checkpoints | Generic primitives | Page states, heartbeat, retry, resume, conflict policies | high | implement now | Atomic I/O/SQLite; interruption tests |
| UF-008 | validation/preview | Metric helpers only | Decode/checksum/blank/collision checks, quarantine, visual previews | high | implement now | Pillow; corrupt/blank/path tests |
| UF-009 | evaluation CLI | CER/WER functions exist, execution reserved | Evaluate manifests/runs and grouped reports | high | implement now | Existing metric policy; golden tests |
| UF-010 | `clouda_training.cli` | Plan only | Validate, split, export, statistics, estimate storage | high | implement now | License gate; leakage/dedup tests |
| UF-011 | `pdfword.engines.FeatureFlaggedLocalModelEngine` | Generic injected-provider boundary only | Concrete safe local HTTP/CLI/OpenAI-compatible/Transformers adapters | high | implement safe adapter | Optional dependencies/credentials/hardware; mock tests |
| UF-012 | `pdfword.ocr_pipeline.process_pdf` | Runtime hook exists; default stays pending | Configure adapters and exercise scanned-page mock path | high | implement safe adapter | No weights/network; mixed-PDF tests |
| UF-013 | lifecycle commands | Temporary cleanup is immediate and narrow | Dry-run-first cleanup/archive/verify with confirmation | medium | implement now | Data-loss risk; lifecycle tests |
| UF-014 | data administration UI | Absent | Local-only isolated Streamlit administration page | medium | implement now | Streamlit; bind-address warning/smoke test |
| UF-015 | worker/Redis hardening | Queue isolation and header rotation exist | Metrics, heartbeat, TLS/auth hooks, rate-limit abstraction | medium | implement safe adapter | External Redis/TLS/SSO; mocked tests |
| UF-016 | OCR model selection/weights | Disabled/unresolved | Load an approved pinned real model | external | legal approval required | License, weights, GPU and human evaluation |
| UF-017 | production SSO/TLS | Boundary/documentation only | Bind real OIDC provider and certificate | external | credentials required | Identity provider, domain, secrets |
| UF-018 | paid cloud/GPU execution | Templates/placeholders | Provision and operate cloud/GPU training | external | hardware required | Paid account and approved model/data |
| UF-019 | actual model training | Explicitly raises `TrainingExecutionDisabled` | GPU training after approvals | external | legal approval required | Dataset/model approval; expensive and intentionally disabled |

