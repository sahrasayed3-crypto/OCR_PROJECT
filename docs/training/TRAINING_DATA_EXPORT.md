# Training data export

Status: **complete for preparation; GPU training remains disabled**.

Exports support generic JSONL, multimodal conversation JSONL, plain OCR,
Markdown, layout, word bounding boxes, and reading order. Each record retains
image URI, instruction, exact target, dataset/document/page/generated IDs,
profile, license, attribution, split, checksum, and schema version.

Commercial export fails closed unless the catalog status and explicit
commercial flag both allow it. Synthetic acceptance data may be exported only
with `--purpose evaluation`. Export never starts training.

