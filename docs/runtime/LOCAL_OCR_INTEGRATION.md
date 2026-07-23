# Local OCR integration

Status: **complete behind a disabled-by-default feature flag**.

Digital PDF text extraction remains first and unchanged. When a scanned page
is detected and local OCR is enabled, the page is rendered within limits,
passed to the configured adapter, checked for non-empty text and bounded
confidence, and recorded with model identity, revision, time, and quality
metadata. Low-quality or failed results require manual review. Mixed PDFs keep
their original page order.

Without a configured, available, pinned local engine, scanned pages remain
`pending_ocr_model`. No real model is selected or downloaded automatically.

