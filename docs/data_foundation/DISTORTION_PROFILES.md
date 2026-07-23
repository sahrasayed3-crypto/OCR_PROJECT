# Distortion profiles

Status: **complete**. Version-1 YAML profiles live in
`configs/data_foundation/distortions` and validate against
`schemas/distortion-profile-v1.schema.json`.

Profiles declare purpose, severity, deterministic seed policy, transformations,
probabilities, parameter ranges, exclusions, maximum dimensions, expected
variants, license restrictions, and visual-quality class. Profiles include
modern scans, old books, weak scans, tiny Arabic text, footnotes, margins,
binding shadows, photocopies, JPEG damage, low DPI, mixed language, and
extreme manual review.

Validate a profile:

```powershell
python -m clouda_data.pipeline.cli validate-distortion-profile modern_scan_medium
```

