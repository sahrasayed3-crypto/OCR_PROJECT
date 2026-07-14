# Data Pipeline Plan

## Data Sources

- Allowed: synthetic pages, self-created fixtures, public-domain material with documented status, and materials with written permission.
- Pending: any external collection whose redistribution, training, or evaluation rights are not yet documented.
- Prohibited for now: copyrighted books, private scans, personal documents, or datasets with unclear license terms.

## Pair Format

- Store image/text pairs with stable IDs.
- Keep the original page image separate from normalized text.
- Record language, script, source, license, permission status, hash, and split.
- Preserve full-page context so margins, footnotes, page numbers, and reading order can be evaluated.

## Splits And Leakage Control

- Use train, validation, and test splits by source document, not by adjacent pages from the same source.
- Keep the final test set frozen and versioned.
- Record file hashes and manifests for reproducibility.
- Do not tune preprocessing or model selection on the final test set.

## Page Categories

- Arabic modern print.
- Arabic historical or degraded print.
- English print.
- Mixed Arabic-English pages.
- Footnotes, marginalia, headers, footers, page numbers, blank pages, and near-blank pages.
- Weak and medium-quality scanned pages.

## Synthetic Degradation

Use controlled augmentation only when the clean source is allowed:

- blur
- noise
- skew
- JPEG compression
- shadows
- yellowing
- bleed-through
- uneven lighting
- edge degradation

Record whether degradation is generated on the fly or pre-generated, and keep the random seed when possible.

## Storage

- Do not commit datasets, original scans, model weights, checkpoints, or large generated outputs.
- Store large data in a controlled object store only after license review.
- Keep manifests, hashes, and small documentation in Git.
- Do not upload private or unlicensed data to cloud services.
